
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def setup_feedback_table():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Missing Supabase credentials")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Supabase Python client doesn't support creating tables directly via API usually
    # But we can try to insert a dummy row or check if it exists
    try:
        # Check if table exists
        res = supabase.table("unanswered_questions").select("*").limit(1).execute()
        print("Table 'unanswered_questions' already exists.")
    except Exception as e:
        print(f"Table might not exist or error: {e}")
        print("Please ensure 'unanswered_questions' table is created in Supabase Dashboard with columns: id, query, confidence_score, created_at, user_id")

if __name__ == "__main__":
    asyncio.run(setup_feedback_table())
