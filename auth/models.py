from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationInfo
from typing import Optional


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: str = Field(..., pattern="^(student|admin)$")
    name: str = Field(..., min_length=2)
    student_id: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v
    
    @field_validator('student_id')
    @classmethod
    def validate_student_id(cls, v, info: ValidationInfo):
        if info.data.get('role') == 'student' and not v:
            raise ValueError('Student ID is required for student role')
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
    type: str = "signup"



class LoginResponse(BaseModel):
    access_token: str
    role: str
    user_id: str
    email: str
    name: str


class ValidateResponse(BaseModel):
    valid: bool
    role: str
    user_id: str
    email: str
    name: Optional[str] = None
