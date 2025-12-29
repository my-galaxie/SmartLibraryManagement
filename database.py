from supabase import create_client, Client
from config import settings


# Initialize Supabase client
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)


def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return supabase


# Service client with admin privileges (if service key is provided)
service_client: Client = None
if settings.supabase_service_key:
    service_client = create_client(settings.supabase_url, settings.supabase_service_key)


def get_service_client() -> Client:
    """Get Supabase service client with admin privileges"""
    if not service_client:
        raise ValueError("Service key not configured")
    return service_client
