import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not url or not key:
    raise ValueError(
"Missing SUPABASE_URL or SUPABASE_PUBLISHABLE_KEY in .env"
)

supabase = create_client(url, key)

try:
    supabase.table("documents").select("id").limit(1).execute()
    print("Supabase connection successful!")
    print("Documents table is accessible.")
except Exception as e:
    print("Supabase connection or table access failed.")
    print("Error:", e)
