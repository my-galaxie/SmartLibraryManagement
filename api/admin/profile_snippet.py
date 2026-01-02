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
