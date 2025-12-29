from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern="^(student|admin)$")
    name: str
    student_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


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
