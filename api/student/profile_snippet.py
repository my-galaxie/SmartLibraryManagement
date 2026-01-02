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
