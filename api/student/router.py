from fastapi import APIRouter, Depends, HTTPException
from api.dependencies import get_student_user
from database import get_supabase_client
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/student", tags=["Student"])


@router.get("/dashboard")
async def get_student_dashboard(current_user: dict = Depends(get_student_user)):
    """
    Get student dashboard summary with borrowed books count, due soon, overdue, and total fines
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["user_id"]
        
        # Get currently borrowed books
        borrowed_response = supabase.table("borrows")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("status", "borrowed")\
            .execute()
        
        borrowed_books = borrowed_response.data if borrowed_response.data else []
        borrowed_count = len(borrowed_books)
        
        # Count due soon (within 3 days) and Calculate dynamic fines
        due_soon_count = 0
        overdue_count = 0
        dynamic_fine = 0
        
        # specific timezone
        tz = ZoneInfo("Asia/Kolkata")
        now = datetime.now(tz)
        
        for borrow in borrowed_books:
            # Handle potential Z suffix and ensure timezone awareness
            due_date_str = borrow["due_date"].replace('Z', '+00:00')
            due_date = datetime.fromisoformat(due_date_str).astimezone(tz)
            
            # Calculate difference in days (using date() to ignore time)
            days_diff = (now.date() - due_date.date()).days
            
            if days_diff > 0:
                overdue_count += 1
                # Calculate fine: 5 Rs per day overdue
                fine_amount = days_diff * 5
                dynamic_fine += fine_amount
            elif days_diff >= -3:
                # Due within next 3 days (days_diff is negative or zero)
                due_soon_count += 1
        
        # Get pending fines from database (fines already charged)
        fines_response = supabase.table("fines")\
            .select("amount")\
            .eq("user_id", user_id)\
            .eq("status", "pending")\
            .execute()
        
        persisted_fine = sum(fine["amount"] for fine in (fines_response.data or []))
        
        # Total fine is potential/dynamic fine + already charged pending fines
        total_fine = dynamic_fine + persisted_fine
        
        return {
            "summary": {
                "currently_borrowed": borrowed_count,
                "due_soon": due_soon_count,
                "overdue": overdue_count,
                "total_fine": float(total_fine)
            }
        }
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/books/current")
async def get_current_borrowed_books(current_user: dict = Depends(get_student_user)):
    """
    Get currently borrowed books for the student
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["user_id"]
        
        # Get borrowed books with book details
        response = supabase.table("borrows")\
            .select("*, books(*)")\
            .eq("user_id", user_id)\
            .eq("status", "borrowed")\
            .order("borrow_date", desc=True)\
            .execute()
        
        if not response.data:
            return {"books": []}
        
        # Format response
        borrowed_books = []
        tz = ZoneInfo("Asia/Kolkata")
        now = datetime.now(tz)
        
        for borrow in response.data:
            book = borrow.get("books", {})
            try:
                # Handle potential Z suffix and ensure timezone awareness
                due_date_str = borrow["due_date"].replace('Z', '+00:00')
                due_date = datetime.fromisoformat(due_date_str).astimezone(tz)
                days_remaining = (due_date.date() - now.date()).days
                
                # Determine status based on days remaining
                if days_remaining < 0:
                    status = "overdue"
                elif days_remaining <= 3:
                    status = "due_soon"
                else:
                    status = "safe"
            except Exception as e:
                logger.error(f"Date parsing error for borrow {borrow['id']}: {e}")
                days_remaining = 0
                status = "unknown"
            
            borrowed_books.append({
                "borrow_id": borrow["id"],
                "book_id": book.get("id"),
                "title": book.get("title"),
                "author": book.get("author"),
                "borrow_date": borrow["borrow_date"],
                "due_date": borrow["due_date"],
                "days_remaining": days_remaining,
                "status": status,
                "fine_amount": float(borrow.get("fine_amount", 0))
            })
        
        return {"books": borrowed_books}
    
    except Exception as e:
        logger.error(f"Current books error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/books/history")
async def get_borrow_history(current_user: dict = Depends(get_student_user)):
    """
    Get complete borrow history for the student
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["user_id"]
        
        response = supabase.table("borrows")\
            .select("*, books(*)")\
            .eq("user_id", user_id)\
            .order("borrow_date", desc=True)\
            .execute()
        
        if not response.data:
            return {"history": []}
        
        history = []
        for borrow in response.data:
            book = borrow.get("books", {})
            
            # Determine if returned on time
            # Determine if returned on time
            returned_status = None
            if borrow["return_date"]:
                try:
                    tz = ZoneInfo("Asia/Kolkata")
                    return_date_str = borrow["return_date"].replace('Z', '+00:00')
                    due_date_str = borrow["due_date"].replace('Z', '+00:00')
                    
                    return_date = datetime.fromisoformat(return_date_str).astimezone(tz)
                    due_date = datetime.fromisoformat(due_date_str).astimezone(tz)
                    
                    returned_status = "on_time" if return_date <= due_date else "late"
                except Exception as e:
                    logger.error(f"Date comparison error in history: {e}")
                    returned_status = "unknown"
            
            history.append({
                "borrow_id": borrow["id"],
                "book_id": book.get("id"),
                "title": book.get("title"),
                "author": book.get("author"),
                "borrow_date": borrow["borrow_date"],
                "due_date": borrow["due_date"],
                "return_date": borrow.get("return_date"),
                "status": borrow["status"],
                "returned_status": returned_status,
                "fine_amount": float(borrow.get("fine_amount", 0))
            })
        
        return {"history": history}
    
    except Exception as e:
        logger.error(f"Borrow history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications")
async def get_student_notifications(current_user: dict = Depends(get_student_user)):
    """
    Get all notifications for the student
    """
    try:
        # Use service client to ensure we can fetch notifications regardless of RLS
        from database import get_service_client
        supabase = get_service_client()
        user_id = current_user["user_id"]
        
        response = supabase.table("notifications")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()
        
        notifications = response.data if response.data else []
        
        # Calculate unread count
        unread_count = sum(1 for n in notifications if not n.get("is_read", False))
        
        return {
            "notifications": notifications,
            "unread_count": unread_count
        }
    
    except Exception as e:
        logger.error(f"Notifications error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_student_user)):
    """
    Mark a notification as read
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["user_id"]
        
        # Verify notification belongs to user
        check_response = supabase.table("notifications")\
            .select("id")\
            .eq("id", notification_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if not check_response.data:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        # Mark as read
        response = supabase.table("notifications")\
            .update({"is_read": True})\
            .eq("id", notification_id)\
            .execute()
        
        return {"message": "Notification marked as read"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mark notification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fines")
async def get_student_fines(current_user: dict = Depends(get_student_user)):
    """
    Get fine summary for the student
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["user_id"]
        
        response = supabase.table("fines")\
            .select("*, borrows(*, books(*))")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        
        if not response.data:
            return {
                "total_pending": 0,
                "total_paid": 0,
                "fines": []
            }
        
        fines_list = []
        total_pending = 0
        total_paid = 0
        
        for fine in response.data:
            borrow = fine.get("borrows", {})
            book = borrow.get("books", {}) if borrow else {}
            
            fine_data = {
                "fine_id": fine["id"],
                "amount": float(fine["amount"]),
                "days_overdue": fine["days_overdue"],
                "status": fine["status"],
                "book_title": book.get("title"),
                "created_at": fine["created_at"],
                "paid_date": fine.get("paid_date")
            }
            fines_list.append(fine_data)
            
            if fine["status"] == "pending":
                total_pending += fine["amount"]
            elif fine["status"] == "paid":
                total_paid += fine["amount"]
        
        return {
            "total_pending": float(total_pending),
            "total_paid": float(total_paid),
            "fines": fines_list
        }
    
    except Exception as e:
        logger.error(f"Fines error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/books/search")
async def search_books(
    query: str = None,
    availability: str = None,
    category: str = None,
    current_user: dict = Depends(get_student_user)
):
    """
    Search books by title, author, or subject with filters
    """
    try:
        supabase = get_supabase_client()
        
        # Base query
        db_query = supabase.table("books").select("*")
        
        # Apply search query
        if query:
            # PostgreSQL ilike syntax for multiple columns needs OR logic which Supabase checks via 'or' filter
            # syntax: .or_('title.ilike.%query%,author.ilike.%query%,subject.ilike.%query%')
            search_param = f"title.ilike.%{query}%,author.ilike.%{query}%,subject.ilike.%{query}%"
            db_query = db_query.or_(search_param)
        
        # Apply availability filter
        if availability == "available":
            db_query = db_query.gt("available_copies", 0)
        elif availability == "unavailable":
            db_query = db_query.eq("available_copies", 0)
            
        # Apply category/subject filter
        if category and category != "all-categories":
            # Mapping frontend values to DB values if needed, or assuming direct match
            if category == "cs":
                db_query = db_query.ilike("subject", "%Computer Science%")
            elif category == "programming":
                 db_query = db_query.ilike("subject", "%Programming%")
            elif category == "se":
                 db_query = db_query.ilike("subject", "%Software Engineering%")
            else:
                 db_query = db_query.ilike("subject", f"%{category}%")

        response = db_query.execute()
        
        books = []
        if response.data:
            for book in response.data:
                books.append({
                    "id": book["id"],
                    "title": book["title"],
                    "author": book["author"],
                    "subject": book["subject"],
                    "available": book["available_copies"],
                    "total": book["total_copies"],
                    "description": book.get("description", "")
                })
                
        return {"books": books}

    except Exception as e:
        logger.error(f"Search books error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/books/{book_id}")
async def get_book_details(
    book_id: str,
    current_user: dict = Depends(get_student_user)
):
    """
    Get detailed information for a specific book
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("books")\
            .select("*")\
            .eq("id", book_id)\
            .single()\
            .execute()
            
        if not response.data:
            raise HTTPException(status_code=404, detail="Book not found")
            
        return {"book": response.data}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get book details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profile/request")
async def request_profile_update(
    request: dict,
    current_user: dict = Depends(get_student_user)
):
    """
    Submit a profile update request
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["user_id"]
        
        # Check for existing pending request
        pending_check = supabase.table("profile_requests")\
            .select("id")\
            .eq("user_id", user_id)\
            .eq("status", "pending")\
            .execute()
            
        if pending_check.data:
            # Update existing pending request
            request_id = pending_check.data[0]["id"]
            response = supabase.table("profile_requests")\
                .update({"requested_changes": request, "updated_at": datetime.now().isoformat()})\
                .eq("id", request_id)\
                .execute()
            return {"message": "Profile update request updated", "id": request_id}
        else:
            # Create new request
            response = supabase.table("profile_requests")\
                .insert({
                    "user_id": user_id,
                    "requested_changes": request,
                    "status": "pending"
                })\
                .execute()
            return {"message": "Profile update request submitted", "id": response.data[0]["id"]}

    except Exception as e:
        logger.error(f"Profile request error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile")
async def get_student_profile(
    current_user: dict = Depends(get_student_user)
):
    """
    Get current user's profile information
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["user_id"]
        
        response = supabase.table("user_profiles")\
            .select("*")\
            .eq("id", user_id)\
            .single()\
            .execute()
            
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")
            
        return {"profile": response.data}
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    student_id: Optional[str] = None


@router.put("/profile")
async def update_student_profile(
    request: ProfileUpdateRequest,
    current_user: dict = Depends(get_student_user)
):
    """
    Update current user's profile information directly
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["user_id"]
        
        updates = {}
        if request.name:
            updates["name"] = request.name
        if request.student_id:
            updates["student_id"] = request.student_id
            
        if not updates:
            raise HTTPException(status_code=400, detail="No changes provided")
            
        response = supabase.table("user_profiles")\
            .update(updates)\
            .eq("id", user_id)\
            .execute()
            
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found or update failed")
            
        return {"message": "Profile updated successfully", "profile": response.data[0]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/request")
async def get_profile_request(
    current_user: dict = Depends(get_student_user)
):
    """
    Get current user's profile request status
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["user_id"]
        
        response = supabase.table("profile_requests")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
            
        if not response.data:
            return {"request": None}
            
        return {"request": response.data[0]}

    except Exception as e:
        logger.error(f"Get profile request error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
