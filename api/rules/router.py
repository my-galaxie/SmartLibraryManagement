from fastapi import APIRouter
from database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rules", tags=["Rules"])


@router.get("/borrow-policy")
async def get_borrow_policy():
    """
    Get borrowing policy and rules
    """
    try:
        supabase = get_supabase_client()
        
        # Get configuration from database
        response = supabase.table("system_config")\
            .select("*")\
            .in_("key", ["borrow_duration_days", "grace_period_days", "fine_per_day", "max_books_per_student"])\
            .execute()
        
        # Convert to dict
        config = {}
        if response.data:
            for item in response.data:
                config[item["key"]] = item["value"]
        
        return {
            "borrow_duration_days": int(config.get("borrow_duration_days", 14)),
            "grace_period_days": int(config.get("grace_period_days", 2)),
            "fine_per_day": float(config.get("fine_per_day", 5)),
            "max_books_per_student": int(config.get("max_books_per_student", 3))
        }
    
    except Exception as e:
        logger.error(f"Get borrow policy error: {e}")
        # Return default values if database query fails
        return {
            "borrow_duration_days": 14,
            "grace_period_days": 2,
            "fine_per_day": 5.0,
            "max_books_per_student": 3
        }
