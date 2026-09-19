import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("PUBLIC_SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_SERVICE", "")
supabase: Client = create_client(url, key)
