from fastapi import APIRouter, Depends, HTTPException, Query
from api.dependencies import get_admin_user
from database import get_supabase_client
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


class BookCreate(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    subject: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None
    total_copies: int = 1
    description: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    subject: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None
    total_copies: Optional[int] = None
    available_copies: Optional[int] = None
    description: Optional[str] = None


class FineConfigUpdate(BaseModel):
    fine_per_day: Optional[float] = None
    grace_period_days: Optional[int] = None
    borrow_duration_days: Optional[int] = None


class BroadcastNotification(BaseModel):
    title: str
    message: str
    type: str = "announcement"


@router.get("/dashboard")
async def get_admin_dashboard(current_user: dict = Depends(get_admin_user)):
    """
    Get admin dashboard analytics
    """
    try:
        supabase = get_supabase_client()
        
        # Total books
        books_response = supabase.table("books").select("id", count="exact").execute()
        total_books = books_response.count if books_response.count else 0
        
        # Currently borrowed
        borrowed_response = supabase.table("borrows")\
            .select("id", count="exact")\
            .eq("status", "borrowed")\
            .execute()
        currently_borrowed = borrowed_response.count if borrowed_response.count else 0
        
        # Overdue count
        overdue_response = supabase.table("borrows")\
            .select("id", count="exact")\
            .eq("status", "overdue")\
            .execute()
        overdue_count = overdue_response.count if overdue_response.count else 0
        
        # Active students (students with at least one borrow record)
        students_response = supabase.table("user_profiles")\
            .select("id", count="exact")\
            .eq("role", "student")\
            .execute()
        active_students = students_response.count if students_response.count else 0
        
        # Get recent borrows for trends (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_borrows_response = supabase.table("borrows")\
            .select("borrow_date")\
            .gte("borrow_date", seven_days_ago)\
            .execute()
        
        # Group by date
        borrow_trends = {}
        if recent_borrows_response.data:
            for borrow in recent_borrows_response.data:
                date = borrow["borrow_date"][:10]  # Get date part
                borrow_trends[date] = borrow_trends.get(date, 0) + 1
        
        return {
            "total_books": total_books,
            "currently_borrowed": currently_borrowed,
            "overdue_count": overdue_count,
            "active_students": active_students,
            "borrow_trends": borrow_trends
        }
    
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_borrow_logs(
    student_id: Optional[str] = Query(None),
    book_id: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    current_user: dict = Depends(get_admin_user)
):
    """
    Get borrow and return logs with filters
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("borrows").select("*, user_profiles(*), books(*)")
        
        if student_id:
            query = query.eq("user_id", student_id)
        if book_id:
            query = query.eq("book_id", book_id)
        if date_from:
            query = query.gte("borrow_date", date_from)
        if date_to:
            query = query.lte("borrow_date", date_to)
        if action:
            query = query.eq("status", action)
        
        response = query.order("borrow_date", desc=True).limit(100).execute()
        
        return response.data if response.data else []
    
    except Exception as e:
        logger.error(f"Logs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/books")
async def get_all_books(current_user: dict = Depends(get_admin_user)):
    """
    Get all books in inventory
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("books").select("*").order("title").execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Get books error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/books")
async def add_book(book: BookCreate, current_user: dict = Depends(get_admin_user)):
    """
    Add a new book to inventory
    """
    try:
        supabase = get_supabase_client()
        
        book_data = {
            **book.dict(),
            "available_copies": book.total_copies
        }
        
        response = supabase.table("books").insert(book_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to add book")
        
        return response.data[0]
    
    except Exception as e:
        logger.error(f"Add book error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/books/{book_id}")
async def update_book(
    book_id: str,
    book_update: BookUpdate,
    current_user: dict = Depends(get_admin_user)
):
    """
    Update book information
    """
    try:
        supabase = get_supabase_client()
        
        # Only include non-None fields
        update_data = {k: v for k, v in book_update.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase.table("books")\
            .update(update_data)\
            .eq("id", book_id)\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Book not found")
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update book error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/books/{book_id}")
async def delete_book(book_id: str, current_user: dict = Depends(get_admin_user)):
    """
    Delete a book from inventory
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("books").delete().eq("id", book_id).execute()
        
        return {"message": "Book deleted successfully"}
    
    except Exception as e:
        logger.error(f"Delete book error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students")
async def get_all_students(current_user: dict = Depends(get_admin_user)):
    """
    Get list of all students
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("user_profiles")\
            .select("*")\
            .eq("role", "student")\
            .order("name")\
            .execute()
        
        return response.data if response.data else []
    
    except Exception as e:
        logger.error(f"Get students error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students/{student_id}")
async def get_student_details(student_id: str, current_user: dict = Depends(get_admin_user)):
    """
    Get detailed information about a student
    """
    try:
        supabase = get_supabase_client()
        
        # Get student profile
        profile_response = supabase.table("user_profiles")\
            .select("*")\
            .eq("id", student_id)\
            .single()\
            .execute()
        
        if not profile_response.data:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get borrow history
        borrows_response = supabase.table("borrows")\
            .select("*, books(*)")\
            .eq("user_id", student_id)\
            .order("borrow_date", desc=True)\
            .execute()
        
        # Get fines
        fines_response = supabase.table("fines")\
            .select("*")\
            .eq("user_id", student_id)\
            .execute()
        
        total_fines = sum(fine["amount"] for fine in (fines_response.data or []) if fine["status"] == "pending")
        
        return {
            "profile": profile_response.data,
            "borrows": borrows_response.data if borrows_response.data else [],
            "fines": fines_response.data if fines_response.data else [],
            "total_pending_fines": float(total_fines)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get student details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fines")
async def get_all_fines(current_user: dict = Depends(get_admin_user)):
    """
    Get overview of all fines
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("fines")\
            .select("*, user_profiles(*), borrows(*, books(*))")\
            .order("created_at", desc=True)\
            .execute()
        
        return response.data if response.data else []
    
    except Exception as e:
        logger.error(f"Get fines error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/fines/config")
async def update_fine_config(
    config: FineConfigUpdate,
    current_user: dict = Depends(get_admin_user)
):
    """
    Update fine configuration
    """
    try:
        supabase = get_supabase_client()
        
        updates = []
        if config.fine_per_day is not None:
            updates.append({
                "key": "fine_per_day",
                "value": str(config.fine_per_day)
            })
        
        if config.grace_period_days is not None:
            updates.append({
                "key": "grace_period_days",
                "value": str(config.grace_period_days)
            })
        
        if config.borrow_duration_days is not None:
            updates.append({
                "key": "borrow_duration_days",
                "value": str(config.borrow_duration_days)
            })
        
        # Update each config value
        for update in updates:
            supabase.table("system_config")\
                .update({"value": update["value"]})\
                .eq("key", update["key"])\
                .execute()
        
        return {"message": "Fine configuration updated successfully"}
    
    except Exception as e:
        logger.error(f"Update fine config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/broadcast")
async def broadcast_notification(
    notification: BroadcastNotification,
    current_user: dict = Depends(get_admin_user)
):
    """
    Send broadcast notification to all students
    """
    try:
        supabase = get_supabase_client()
        
        # Get all students
        students_response = supabase.table("user_profiles")\
            .select("id")\
            .eq("role", "student")\
            .execute()
        
        if not students_response.data:
            return {"message": "No students found"}
        
        # Create notifications for all students
        notifications = []
        for student in students_response.data:
            notifications.append({
                "user_id": student["id"],
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "is_read": False
            })
        
        response = supabase.table("notifications").insert(notifications).execute()
        
        return {
            "message": f"Notification sent to {len(notifications)} students"
        }
    
    except Exception as e:
        logger.error(f"Broadcast notification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
