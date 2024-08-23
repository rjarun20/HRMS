import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from ..services.auth_service import AuthService
from ..exceptions import AuthenticationError

logger = logging.getLogger(__name__)

def login_view(request):
        # Clear any existing messages
    storage = get_messages(request)
    for message in storage:
        pass
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "You must provide both an email and a password.")
            return render(request, 'accounts/login.html')
        
        try:
            user_data = AuthService.login(email, password)
            request.session['user'] = user_data
            request.session['is_admin'] = user_data.get('user_metadata', {}).get('is_admin', False)
            request.session['access_token'] = user_data['access_token']
            messages.success(request, f"Welcome back, {email}!")
            django_user, created = User.objects.get_or_create(username=email)
            auth_login(request, django_user)
            return redirect('accounts:home')
        except AuthenticationError as e:
            logger.error(f"Login error for user {email}: {str(e)}")
            messages.error(request, str(e))
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    try:
        AuthService.logout()
        auth_logout(request)
        messages.success(request, "You have been logged out successfully.")
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        messages.error(request, f"An error occurred during logout: {str(e)}")
    
    return redirect('accounts:home')