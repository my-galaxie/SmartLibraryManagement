import asyncio
import os
from database import get_service_client
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_search():
    print("--- DEBUGGING SUPABASE SEARCH ---")
    try:
        supabase = get_service_client()
        
        # Test 1: Simple Select (Control)
        print("\n1. Testing Simple Select (No filters)...")
        res = supabase.table("books").select("id, title").limit(1).execute()
        print(f"Success: Found {len(res.data)} books")
        
        # Test 2: ILIKE with % (Current Approach)
        print("\n2. Testing ILIKE with '%' (Current Code)...")
        try:
            res = supabase.table("books").select("id, title")\
                .ilike("title", "%Introduction%")\
                .execute()
            print(f"Success: Found {len(res.data)} books")
        except Exception as e:
            print(f"FAILED: {e}")

        # Test 3: ILIKE with * (PostgREST Wildcard?)
        print("\n3. Testing ILIKE with '*'...")
        try:
            res = supabase.table("books").select("id, title")\
                .ilike("title", "*Introduction*")\
                .execute()
            print(f"Success: Found {len(res.data)} books")
        except Exception as e:
            print(f"FAILED: {e}")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(debug_search())
