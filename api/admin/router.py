from fastapi import APIRouter, Depends, HTTPException, Query
from api.dependencies import get_admin_user
import re
from database import get_supabase_client, get_service_client
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
    reminder_days: Optional[int] = None
    overdue_frequency: Optional[str] = None


class BroadcastNotification(BaseModel):
    title: str
    message: str
    type: str = "announcement"

    @property
    def valid_types(self):
        return ["due_soon", "overdue", "availability", "announcement", "system"]

    def validate_type(self):
        if self.type not in self.valid_types:
            raise ValueError(f"Invalid type. Must be one of: {', '.join(self.valid_types)}")



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
        
        # Total copies
        copies_response = supabase.table("books").select("total_copies").execute()
        total_copies = sum(book["total_copies"] for book in copies_response.data) if copies_response.data else 0

        # Borrowed today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        borrowed_today_response = supabase.table("borrows")\
            .select("id", count="exact")\
            .gte("borrow_date", today_start)\
            .execute()
        borrowed_today = borrowed_today_response.count if borrowed_today_response.count else 0

        # Total fines
        fines_response = supabase.table("fines").select("amount").execute()
        total_fines = sum(fine["amount"] for fine in fines_response.data) if fines_response.data else 0
        
        # Recent borrows list
        recent_borrows_list_response = supabase.table("borrows")\
            .select("*, books(title), user_profiles(name, student_id)")\
            .order("borrow_date", desc=True)\
            .limit(5)\
            .execute()
        recent_borrows = recent_borrows_list_response.data if recent_borrows_list_response.data else []


        # Group by date for borrow trends (last 7 days)
        borrow_trends_data = []
        today = datetime.now().date()
        for i in range(6, -1, -1):
             date_val = today - timedelta(days=i)
             date_str = date_val.isoformat()
             day_name = date_val.strftime("%a") # Mon, Tue
             count = borrow_trends.get(date_str, 0)
             borrow_trends_data.append({"day": day_name, "borrows": count})

        # Overdue trends (last 6 months - mock for now or calculate if possible)
        # Real calculation would need historical overdue logs which we might not have fully tracked
        # We will query borrows table where status=overdue created_at in range
        # For now, let's just return what we can or kept it static if data model is limited
        # But user wants real data. Let's try to query metrics if possible.
        # Check 'fines' table creation date for proxy of overdue incidents?
        
        overdue_trends_data = []
        # Simple proxy: count fines by month
        six_months_ago = (datetime.now() - timedelta(days=180)).isoformat()
        fines_trend_res = supabase.table("fines")\
            .select("created_at")\
            .gte("created_at", six_months_ago)\
            .execute()
            
        fines_by_month = {}
        if fines_trend_res.data:
            for fine in fines_trend_res.data:
                # Format: YYYY-MM
                month_key = fine["created_at"][:7]
                fines_by_month[month_key] = fines_by_month.get(month_key, 0) + 1
        
        # Fill last 6 months
        for i in range(5, -1, -1):
            d = today - timedelta(days=i*30)
            m_key = d.strftime("%Y-%m")
            m_name = d.strftime("%b")
            overdue_trends_data.append({"month": m_name, "overdue": fines_by_month.get(m_key, 0)})

        return {
            "summary": {
                "total_books": total_books,
                "total_copies": total_copies,
                "borrowed_today": borrowed_today,
                "active_borrows": currently_borrowed,
                "overdue_borrows": overdue_count,
                "total_students": active_students,
                "total_fines": total_fines
            },
            "recent_borrows": recent_borrows,
            "borrow_trends": borrow_trends_data,
            "overdue_trends": overdue_trends_data
        }
    
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug-borrows")
async def debug_borrows(current_user: dict = Depends(get_admin_user)):
    """Temporary debug endpoint to check borrows table"""
    supabase = get_service_client()
    res = supabase.table("borrows").select("*", count="exact").execute()
    return {
        "count": res.count,
        "data": res.data
    }


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
        # Use service client to bypass RLS
        supabase = get_service_client()
        
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
            
        # Log the query execution
        logger.info(f"Executing log query with filters: student_id={student_id}, book_id={book_id}")
            
        response = query.order("borrow_date", desc=True).execute()
        
        logger.info(f"Log query result count: {len(response.data) if response.data else 0}")
        if response.data:
            logger.info(f"Sample log: {response.data[0]}")
            
        logs = response.data if response.data else []
        return {
            "logs": logs,
            "total": len(logs)
        }
    
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
        books = response.data if response.data else []
        return {
            "books": books,
            "total": len(books)
        }
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
        
        return {
    "message": "Book added successfully",
    "book": response.data[0]
}

    
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
        
        return {
    "message": "Book updated successfully",
    "book": response.data[0]
}

    
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
        # Use service client to bypass RLS
        supabase = get_service_client()
        
        # Get all students
        response = supabase.table("user_profiles")\
            .select("*")\
            .eq("role", "student")\
            .order("name")\
            .execute()
        
        students_data = response.data if response.data else []
        
        # Calculate stats for each student
        students_with_stats = []
        for student in students_data:
            user_id = student["id"]
            
            # Active borrows count
            borrows_res = supabase.table("borrows")\
                .select("id", count="exact")\
                .eq("user_id", user_id)\
                .eq("status", "borrowed")\
                .execute()
            active_borrows = borrows_res.count if borrows_res.count else 0
            
            # Total fines count
            fines_res = supabase.table("fines")\
                .select("amount")\
                .eq("user_id", user_id)\
                .execute()
            total_fines = sum(f["amount"] for f in fines_res.data) if fines_res.data else 0
            
            students_with_stats.append({
                "id": student["id"],
                "email": student["email"],
                "name": student["name"],
                "student_id": student.get("student_id"),
                "active_borrows": active_borrows,
                "total_fines": total_fines
            })
            
        return {
            "students": students_with_stats,
            "total": len(students_with_stats)
        }
    
    except Exception as e:
        logger.error(f"Get students error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students/{student_id}")
async def get_student_details(student_id: str, current_user: dict = Depends(get_admin_user)):
    """
    Get detailed information about a student
    """
    try:
        # Use service client to bypass RLS
        supabase = get_service_client()
        
        # Check if input is UUID or student_id string
        is_uuid = re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', student_id)
        
        query = supabase.table("user_profiles").select("*")
        
        if is_uuid:
            query = query.eq("id", student_id)
        else:
            query = query.eq("student_id", student_id)
            
        profile_response = query.single().execute()
        
        if not profile_response.data:
            raise HTTPException(status_code=404, detail="Student not found")
        
        student = profile_response.data
        user_id = student["id"]
        
        # Get active borrows
        borrows_response = supabase.table("borrows")\
            .select("*, books(title, author)")\
            .eq("user_id", user_id)\
            .eq("status", "borrowed")\
            .execute()
        
        active_borrows = borrows_response.data if borrows_response.data else []
        
        # Get borrow history
        history_response = supabase.table("borrows")\
            .select("*, books(title, author)")\
            .eq("user_id", user_id)\
            .neq("status", "borrowed")\
            .order("borrow_date", desc=True)\
            .limit(10)\
            .execute()
            
        history = history_response.data if history_response.data else []
        
        return {
            "student": student,
            "active_borrows": active_borrows,
            "history": history
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
        
        fines = response.data if response.data else []
        return {
            "fines": fines,
            "total_count": len(fines),
            "total_amount": sum(float(f["amount"]) for f in fines)
        }
    
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

        if config.reminder_days is not None:
            updates.append({
                "key": "reminder_days",
                "value": str(config.reminder_days)
            })

        if config.overdue_frequency is not None:
            updates.append({
                "key": "overdue_frequency",
                "value": str(config.overdue_frequency)
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
        # Validate type
        if notification.type not in ["due_soon", "overdue", "availability", "announcement", "system"]:
             # Fallback to announcement if invalid
             notification.type = "announcement"
        
        # Use service client to bypass RLS
        supabase = get_service_client()
        
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


@router.get("/notifications/history")
async def get_notification_history(current_user: dict = Depends(get_admin_user)):
    """
    Get history of sent broadcast notifications
    """
    try:
        supabase = get_supabase_client()
        
        # Get recent announcements (limit to last 50 to process)
        # distinct() is not directly available in standard postgrest-py builder easily in this version maybe?
        # We fetch all announcement type notifications ordered by time
        
        response = supabase.table("notifications")\
            .select("title, message, created_at, type")\
            .eq("type", "announcement")\
            .order("created_at", desc=True)\
            .limit(100)\
            .execute()
            
        if not response.data:
            return {"notifications": []}
            
        # Deduplicate in python
        # Group by (title, message, created_at minute) to avoid duplicates for same broadcast
        unique_notifications = []
        seen = set()
        
        for notif in response.data:
            # Create a signature. created_at might differ by milliseconds if inserted sequentially, 
            # but usually for a broadcast they are close. 
            # Or simplified: checking title+message. 
            # If a user sends same message twice, we might dedupe it unintentionally if we ignore time.
            # Let's use first 16 chars of timestamp (min resolution)
            
            ts = notif["created_at"][:16] # YYYY-MM-DDTHH:MM
            sig = (notif["title"], notif["message"], ts)
            
            if sig not in seen:
                seen.add(sig)
                unique_notifications.append({
                    "id": f"{ts}-{len(seen)}", # Generate a temp id
                    "title": notif["title"],
                    "message": notif["message"],
                    "created_at": notif["created_at"],
                    "type": notif["type"]
                })
        
        return {"notifications": unique_notifications[:20]} # Return top 20
        
    except Exception as e:
        logger.error(f"Notification history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/requests")
async def get_profile_requests(
    current_user: dict = Depends(get_admin_user)
):
    """
    Get all pending profile update requests
    """
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("profile_requests")\
            .select("*, user_profiles(name, email, student_id)")\
            .eq("status", "pending")\
            .order("created_at", desc=True)\
            .execute()
            
        return {"requests": response.data if response.data else []}

    except Exception as e:
        logger.error(f"Get profile requests error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profile/requests/{request_id}/{action}")
async def process_profile_request(
    request_id: str,
    action: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Approve or reject a profile update request.
    Action: 'approve' or 'reject'
    """
    try:
        supabase = get_supabase_client()
        admin_id = current_user["user_id"]
        
        if action not in ["approve", "reject"]:
            raise HTTPException(status_code=400, detail="Invalid action")
            
        # Get the request
        req_response = supabase.table("profile_requests")\
            .select("*")\
            .eq("id", request_id)\
            .single()\
            .execute()
            
        if not req_response.data:
            raise HTTPException(status_code=404, detail="Request not found")
            
        request_data = req_response.data
        
        if action == "approve":
            # Update user profile
            changes = request_data["requested_changes"]
            # Filter allowed fields to prevent arbitrary updates (e.g. role)
            allowed_fields = ["name", "student_id", "email", "phone"]
            updates = {k: v for k, v in changes.items() if k in allowed_fields}
            
            if updates:
                user_update = supabase.table("user_profiles")\
                    .update(updates)\
                    .eq("id", request_data["user_id"])\
                    .execute()
                    
        # Update request status
        status_update = supabase.table("profile_requests")\
            .update({
                "status": "approved" if action == "approve" else "rejected",
                "reviewed_by": admin_id,
                "updated_at": datetime.now().isoformat()
            })\
            .eq("id", request_id)\
            .execute()
            
        return {"message": f"Request {action}d successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process request error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
