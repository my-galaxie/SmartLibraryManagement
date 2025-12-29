from fastapi import APIRouter, Depends, Query
from api.dependencies import get_current_user
from database import get_supabase_client
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("")
async def list_resources(
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
        supabase = get_supabase_client()
        
        query = supabase.table("resources").select("*")
        
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
