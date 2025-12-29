from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from database import get_supabase_client, get_service_client
from config import settings
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service using Supabase"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return payload
        except JWTError as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    @staticmethod
    async def signup(email: str, password: str, role: str, name: str, student_id: Optional[str] = None) -> dict:
        """Register new user"""
        try:
            # Use service client for signup to have full access
            service_client = get_service_client()
            
            # Create auth user in Supabase
            auth_response = service_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True  # Auto-confirm email for testing
            })
            
            if not auth_response.user:
                raise ValueError("Failed to create user")
            
            user_id = auth_response.user.id
            logger.info(f"Created user in auth.users with ID: {user_id}")
            
            # Create user profile
            profile_data = {
                "id": user_id,
                "email": email,
                "name": name,
                "role": role,
                "student_id": student_id
            }
            
            # Insert profile with service client to bypass RLS
            try:
                profile_response = service_client.table("user_profiles").insert(profile_data).execute()
                
                if not profile_response.data:
                    raise ValueError("Failed to create user profile - no data returned")
                    
                logger.info(f"Created user profile for {email}")
                
            except Exception as profile_error:
                logger.error(f"Profile creation error: {profile_error}")
                # Try to clean up the auth user if profile creation fails
                try:
                    service_client.auth.admin.delete_user(user_id)
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup auth user: {cleanup_error}")
                raise ValueError(f"Failed to create user profile: {str(profile_error)}")
            
            return {
                "user_id": user_id,
                "email": email,
                "role": role,
                "name": name
            }
            
        except Exception as e:
            logger.error(f"Signup error: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            raise Exception(f"Signup failed: {str(e)}")
    
    @staticmethod
    async def login(email: str, password: str) -> dict:
        """Authenticate user and return token"""
        try:
            supabase = get_supabase_client()
            
            # Authenticate with Supabase
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                raise ValueError("Invalid credentials")
            
            user_id = auth_response.user.id
            
            # Get user profile to fetch role and name
            profile_response = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if not profile_response.data:
                raise ValueError("User profile not found")
            
            profile = profile_response.data[0]
            
            # Create our own JWT token with user info
            token_data = {
                "sub": user_id,
                "email": email,
                "role": profile["role"]
            }
            access_token = AuthService.create_access_token(token_data)
            
            return {
                "access_token": access_token,
                "role": profile["role"],
                "user_id": user_id,
                "email": email,
                "name": profile["name"]
            }
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            logger.error(f"Login error type: {type(e).__name__}")
            logger.error(f"Login error details: {repr(e)}")
            raise Exception(f"Login failed: {str(e)}")
    
    @staticmethod
    async def validate_token(token: str) -> dict:
        """Validate JWT token and return user info"""
        payload = AuthService.verify_token(token)
        
        if not payload:
            raise ValueError("Invalid token")
        
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        
        if not all([user_id, email, role]):
            raise ValueError("Invalid token payload")
        
        return {
            "valid": True,
            "user_id": user_id,
            "email": email,
            "role": role
        }
