import os
from dotenv import load_dotenv
from pathlib import Path

try:
    from supabase import create_client, Client
except ImportError:  # pragma: no cover - handled at runtime
    create_client = None
    Client = None

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def get_supabase_client() -> "Client":
    """Get Supabase client instance"""
    if create_client is None:
        raise ValueError(
            "Supabase client library is not installed. Please add 'supabase' to requirements.txt"
        )
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file"
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)

