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
    async def signup(email: str, password: str, role: str, name: str, student_id: Optional[str] = None, department: Optional[str] = None) -> dict:
        """Register new user"""
        logger.info(f"Attempting signup for email: {email}, role: {role}")
        try:
            # Use service client for signup to have full access
            service_client = get_service_client()
            
            # Create auth user in Supabase
            auth_response = service_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": False  # Use False to trigger email confirmation (depends on Supabase settings)
            })
            
            # If auto-confirm is OFF in Supabase, user is created but email_confirmed_at is null
            # auth_response.user is still returned

            
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
                "student_id": student_id,
                "department": department
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
        logger.info(f"Attempting login for email: {email}")
        try:
            supabase = get_supabase_client()
            
            # Authenticate with Supabase
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user or not auth_response.session:
                raise ValueError("Invalid credentials")
            
            user_id = auth_response.user.id
            access_token = auth_response.session.access_token

            # Get user profile to fetch role and name
            # Note: We use the SERVICE client here to ensure we can read the profile even if RLS is strict
            service_client = get_service_client()
            profile_response = service_client.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if not profile_response.data:
                raise ValueError("User profile not found")
            
            profile = profile_response.data[0]
            
            return {
                "access_token": access_token,
                "role": profile["role"],
                "user_id": user_id,
                "email": email,
                "name": profile["name"]
            }
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise Exception(f"Login failed: {str(e)}")
    
    @staticmethod
    async def validate_token(token: str) -> dict:
        """Validate JWT token and return user info"""
        try:
            supabase = get_supabase_client()
            # Verify with Supabase Auth
            user_response = supabase.auth.get_user(token)
            
            if not user_response.user:
                logger.error(f"Supabase Auth Error: {user_response}")
                raise ValueError(f"Supabase rejected token. Response: {user_response}")
            
            user = user_response.user
            
            # Check Profile
            # Use service client to ensure we can read/write profile
            service_client = get_service_client()
            profile_response = service_client.table("user_profiles").select("*").eq("id", user.id).execute()
            
            if not profile_response.data:
                # First time Google Login (or other OAuth) - Create Profile
                logger.info(f"Profile not found for {user.email}, creating default student profile.")
                try:
                    name = user.user_metadata.get('full_name') or user.user_metadata.get('name') or user.email.split('@')[0]
                    
                    new_profile = {
                        "id": user.id,
                        "email": user.email,
                        "name": name,
                        "role": "student"  # Default role
                    }
                    service_client.table("user_profiles").insert(new_profile).execute()
                    
                    role = "student"
                    profile_name = name
                except Exception as e:
                    logger.error(f"Auto-create profile failed: {e}")
                    raise ValueError("Failed to create user profile")
            else:
                role = profile_response.data[0]['role']
                profile_name = profile_response.data[0]['name']

            return {
                "valid": True,
                "user_id": user.id,
                "email": user.email,
                "role": role,
                "name": profile_name
            }
            
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            # Bubble up the actual error for debugging
            raise ValueError(f"Token validation failed: {str(e)}")

    @staticmethod
    async def verify_otp(email: str, token: str, type: str = "signup") -> dict:
        """Verify OTP/Email verification"""
        try:
            supabase = get_supabase_client()
            response = supabase.auth.verify_otp({
                "email": email,
                "token": token,
                "type": type
            })
            
            if not response.user:
                 raise ValueError("Verification failed")
                 
            return {"message": "Email verified successfully"}
            
        except Exception as e:
            logger.error(f"OTP verification error: {e}")
            raise Exception(f"Verification failed: {str(e)}")
