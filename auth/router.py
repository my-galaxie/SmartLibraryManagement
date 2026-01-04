from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from auth.models import SignupRequest, LoginRequest, LoginResponse, ValidateResponse, VerifyOTPRequest
from auth.service import AuthService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup")
async def signup(request: SignupRequest):
    """
    Register a new user (student or admin)
    """
    try:
        result = await AuthService.signup(
            email=request.email,
            password=request.password,
            role=request.role,
            name=request.name,
            student_id=request.student_id,
            department=request.department
        )
        
        return {
            "message": "Signup successful",
            "user": result
        }
    
    except Exception as e:
        logger.error(f"Signup endpoint error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and issue JWT token
    """
    try:
        result = await AuthService.login(
            email=request.email,
            password=request.password
        )
        
        return LoginResponse(**result)
    
    except ValueError as e:
        # Return specific error for known issues (e.g., "User profile not found")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login endpoint error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/validate", response_model=ValidateResponse)
async def validate(authorization: Optional[str] = Header(None)):
    """
    Validate JWT token from Authorization header
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    try:
        result = await AuthService.validate_token(token)
        return ValidateResponse(**result)
    
    except Exception as e:
        logger.error(f"Validation endpoint error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/logout")
async def logout():
    """
    Logout endpoint (stateless acknowledgment)
    Since we're using stateless JWT, actual logout happens on client side
    """
    return {"message": "Logout successful"}


@router.post("/verify")
async def verify_otp(request: VerifyOTPRequest):
    """
    Verify OTP for email confirmation
    """
    try:
        await AuthService.verify_otp(request.email, request.otp, request.type)
        return {"message": "Verification successful"}
    except Exception as e:
        logger.error(f"Verification endpoint error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

