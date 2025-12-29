from fastapi import APIRouter, Depends, HTTPException, Query
from api.dependencies import get_current_user
from database import get_supabase_client
from typing import Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/books", tags=["Books"])


class AvailabilitySubscription(BaseModel):
    book_id: str


@router.get("/search")
async def search_books(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    availability: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Search books with optional filters
    """
    try:
        supabase = get_supabase_client()
        
        # Start with base query
        query = supabase.table("books").select("*")
        
        # Apply filters
        if title:
            query = query.ilike("title", f"%{title}%")
        if author:
            query = query.ilike("author", f"%{author}%")
        if subject:
            query = query.ilike("subject", f"%{subject}%")
        if category:
            query = query.eq("category", category)
        if availability == "available":
            query = query.gt("available_copies", 0)
        elif availability == "unavailable":
            query = query.eq("available_copies", 0)
        
        response = query.order("title").execute()
        
        return response.data if response.data else []
    
    except Exception as e:
        logger.error(f"Search books error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{book_id}")
async def get_book_details(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific book
    """
    try:
        supabase = get_supabase_client()
        
        # Get book details
        book_response = supabase.table("books")\
            .select("*")\
            .eq("id", book_id)\
            .single()\
            .execute()
        
        if not book_response.data:
            raise HTTPException(status_code=404, detail="Book not found")
        
        book = book_response.data
        
        # Get book copies
        copies_response = supabase.table("book_copies")\
            .select("*")\
            .eq("book_id", book_id)\
            .execute()
        
        copies = copies_response.data if copies_response.data else []
        
        # Check if user has subscribed for availability notification
        subscription_response = supabase.table("availability_subscriptions")\
            .select("id")\
            .eq("user_id", current_user["user_id"])\
            .eq("book_id", book_id)\
            .execute()
        
        has_subscription = len(subscription_response.data) > 0 if subscription_response.data else False
        
        return {
            **book,
            "copies": copies,
            "is_available": book["available_copies"] > 0,
            "user_subscribed": has_subscription
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get book details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{book_id}/notify")
async def subscribe_to_availability(
    book_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Subscribe to availability notification for a book
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["user_id"]
        
        # Check if book exists
        book_response = supabase.table("books")\
            .select("id, title, available_copies")\
            .eq("id", book_id)\
            .single()\
            .execute()
        
        if not book_response.data:
            raise HTTPException(status_code=404, detail="Book not found")
        
        book = book_response.data
        
        # Check if book is already available
        if book["available_copies"] > 0:
            return {
                "message": "Book is currently available",
                "available": True
            }
        
        # Check if already subscribed
        existing_response = supabase.table("availability_subscriptions")\
            .select("id")\
            .eq("user_id", user_id)\
            .eq("book_id", book_id)\
            .execute()
        
        if existing_response.data:
            return {
                "message": "Already subscribed to notifications for this book"
            }
        
        # Create subscription
        subscription_data = {
            "user_id": user_id,
            "book_id": book_id,
            "notified": False
        }
        
        response = supabase.table("availability_subscriptions")\
            .insert(subscription_data)\
            .execute()
        
        return {
            "message": f"You will be notified when '{book['title']}' becomes available"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subscribe to availability error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
