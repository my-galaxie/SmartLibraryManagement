from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: Optional[str] = None
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # API
    api_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    
    # Fine configuration
    fine_per_day: float = 5.0
    grace_period_days: int = 2
    borrow_duration_days: int = 14
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
