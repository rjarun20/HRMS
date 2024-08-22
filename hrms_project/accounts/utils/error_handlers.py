import logging
from django.contrib import messages

logger = logging.getLogger(__name__)

def handle_supabase_error(request, e, action):
    logger.exception(f"Error during {action}: {str(e)}")
    messages.error(request, f"{action} failed: {str(e)}")