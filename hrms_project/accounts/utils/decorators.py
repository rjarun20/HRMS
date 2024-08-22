import logging
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

logger = logging.getLogger(__name__)

def admin_required(view_func):
    """
    Decorator to ensure that only admin users can access the view.
    If the user is not an admin, they are redirected to the home page with an error message.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_data = request.session.get('user', {})
        is_admin = user_data.get('user_metadata', {}).get('is_admin', False)
        if request.user.is_authenticated and is_admin:
            return view_func(request, *args, **kwargs)
        else:
            logger.warning(f"Non-admin user {request.user} attempted to access admin-only view")
            messages.error(request, "You don't have permission to access this page.")
            return redirect('home')
    return wrapper