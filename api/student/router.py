from fastapi import APIRouter, Depends, HTTPException
from api.dependencies import get_student_user
from database import get_supabase_client
from datetime import datetime
import logging

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
        
        # Count due soon (within 3 days)
        due_soon_count = 0
        overdue_count = 0
        now = datetime.now()
        
        for borrow in borrowed_books:
            due_date = datetime.fromisoformat(borrow["due_date"].replace('Z', '+00:00'))
            days_until_due = (due_date - now).days
            
            if days_until_due < 0:
                overdue_count += 1
            elif days_until_due <= 3:
                due_soon_count += 1
        
        # Get total fines
        fines_response = supabase.table("fines")\
            .select("amount")\
            .eq("user_id", user_id)\
            .eq("status", "pending")\
            .execute()
        
        total_fine = sum(fine["amount"] for fine in (fines_response.data or []))
        
        return {
            "borrowed_count": borrowed_count,
            "due_soon": due_soon_count,
            "overdue": overdue_count,
            "total_fine": float(total_fine)
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
            return []
        
        # Format response
        borrowed_books = []
        now = datetime.now()
        
        for borrow in response.data:
            book = borrow.get("books", {})
            due_date = datetime.fromisoformat(borrow["due_date"].replace('Z', '+00:00'))
            days_remaining = (due_date - now).days
            
            # Determine status
            if days_remaining < 0:
                status = "overdue"
            elif days_remaining <= 3:
                status = "due_soon"
            else:
                status = "safe"
            
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
        
        return borrowed_books
    
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
            return []
        
        history = []
        for borrow in response.data:
            book = borrow.get("books", {})
            
            # Determine if returned on time
            returned_status = None
            if borrow["return_date"]:
                return_date = datetime.fromisoformat(borrow["return_date"].replace('Z', '+00:00'))
                due_date = datetime.fromisoformat(borrow["due_date"].replace('Z', '+00:00'))
                returned_status = "on_time" if return_date <= due_date else "late"
            
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
        
        return history
    
    except Exception as e:
        logger.error(f"Borrow history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications")
async def get_student_notifications(current_user: dict = Depends(get_student_user)):
    """
    Get all notifications for the student
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["user_id"]
        
        response = supabase.table("notifications")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()
        
        return response.data if response.data else []
    
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
