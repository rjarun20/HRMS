import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client
SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL or SUPABASE_KEY environment variables are not set")
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_supabase_connection() -> bool:
    """
    Check if the connection to Supabase is working.
    Returns True if connected, False otherwise.
    """
    try:
        # Attempt to fetch a single user to test the connection
        supabase.auth.admin.list_users(page=1, per_page=1)
        logger.info("Successfully connected to Supabase")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {str(e)}")
        return False

# Check connection on startup
if not check_supabase_connection():
    logger.warning("Failed to establish initial connection to Supabase")