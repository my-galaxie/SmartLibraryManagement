from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form
from api.dependencies import get_current_user, get_admin_user
from database import get_supabase_client
from typing import Optional
import logging
import uuid
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("")
async def list_resources(
    title: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    semester: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    List academic resources with filters
    """
    try:
        # Use service client to bypass potentially restricted RLS if public read is not fully open
        from database import get_service_client
        supabase = get_service_client()
        
        query = supabase.table("resources").select("*")
        
        if title:
            # Using custom wildcard search for title
            query = query.ilike("title", f"%{title}%")
        if subject:
            query = query.ilike("subject", f"%{subject}%")
        if semester:
            query = query.eq("semester", semester)
        if year:
            query = query.eq("year", year)
        if type:
            query = query.eq("type", type)
        
        response = query.order("year", desc=True).order("semester", desc=True).execute()
        
        return response.data if response.data else []
    
    except Exception as e:
        logger.error(f"List resources error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def upload_resource(
    title: str = Form(...),
    subject: str = Form(...),
    semester: int = Form(...),
    year: int = Form(...),
    type: str = Form("paper"), # paper, notes, etc
    file: UploadFile = File(...),
    current_user: dict = Depends(get_admin_user)
):
    """
    Upload a new academic resource
    """
    try:
        # Use service client for storage operations to ensure permissions
        from database import get_service_client
        service_client = get_service_client()
        
        # Ensure bucket exists
        try:
            buckets = service_client.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            if "resources" not in bucket_names:
                logger.info("Creating 'resources' bucket...")
                service_client.storage.create_bucket("resources", options={"public": True})
        except Exception as bucket_err:
             logger.warning(f"Bucket check/create failed (might already exist or permission issue): {bucket_err}")

        # 1. Generate unique filename
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = f"{subject}/{semester}/{unique_filename}"
        
        # 2. Read file
        contents = await file.read()
        
        # 3. Upload to Storage using service client
        try:
            storage_response = service_client.storage.from_("resources").upload(
                file_path,
                contents,
                {"content-type": file.content_type}
            )
        except Exception as upload_err:
             logger.error(f"Storage upload failed: {upload_err}")
             raise HTTPException(status_code=500, detail=f"Storage upload failed: {str(upload_err)}")

        # 4. Get Public URL
        public_url_res = service_client.storage.from_("resources").get_public_url(file_path)
        file_url = public_url_res 
        
        # 5. Insert into Database
        resource_data = {
            "title": title,
            "subject": subject,
            "semester": semester,
            "year": year,
            "type": type,
            "file_url": file_url,
            "file_path": file_path,
            "file_size": len(contents),
            "uploaded_by": current_user["user_id"]
        }
        
        db_response = service_client.table("resources").insert(resource_data).execute()
        
        if not db_response.data:
            raise HTTPException(status_code=500, detail="Failed to save resource metadata")
            
        return {
            "message": "Resource uploaded successfully",
            "resource": db_response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload resource error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/{resource_id}/download")
async def download_resource(
    resource_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get download URL for a resource
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("resources")\
            .select("*")\
            .eq("id", resource_id)\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return {
            "download_url": response.data["file_url"],
            "title": response.data["title"],
            "file_size": response.data.get("file_size")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download resource error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Delete a resource
    """
    try:
        from database import get_service_client
        service_client = get_service_client()
        
        # Get resource to find file path
        res = service_client.table("resources").select("*").eq("id", resource_id).single().execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        resource = res.data
        file_path = resource["file_path"]
        
        # Delete from storage
        if file_path:
            try:
                service_client.storage.from_("resources").remove([file_path])
            except Exception as storage_err:
                logger.error(f"Failed to delete file from storage: {storage_err}")
                # Continue to delete metadata even if file delete fails (orphaned file is better than broken UI)
        
        # Delete from database
        service_client.table("resources").delete().eq("id", resource_id).execute()
        
        return {"message": "Resource deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete resource error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
