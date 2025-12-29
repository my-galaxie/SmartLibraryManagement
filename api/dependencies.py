from fastapi import Depends, HTTPException, Header
from typing import Optional
from auth.service import AuthService
import logging

logger = logging.getLogger(__name__)


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Dependency to get current authenticated user from JWT token
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    try:
        user_data = await AuthService.validate_token(token)
        return user_data
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_student_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to ensure user is a student
    """
    if current_user.get("role") != "student":
        raise HTTPException(status_code=403, detail="Access denied: Student role required")
    return current_user


async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to ensure user is an admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admin role required")
    return current_user
