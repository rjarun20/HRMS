from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .supabase_client import supabase

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check that both email and password are provided
        if not email or not password:
            messages.error(request, "You must provide both an email and a password.")
            return render(request, 'accounts/login.html')
        
        try:
            # Supabase authentication
            response = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            
            # Check if login was successful
            if response.user is None:
                messages.error(request, "Login failed: Invalid login credentials.")
            else:
                # Store the entire response object in the session
                request.session['user'] = {
                    'id': response.user.id,
                    'email': response.user.email,
                    'role': response.user.role,
                    'app_metadata': response.user.app_metadata,
                    'user_metadata': response.user.user_metadata,
                }
                request.session['access_token'] = response.session.access_token

                messages.success(request, f"Welcome back, {response.user.email}!")

                # Log in the user using Django's auth system
                django_user, created = User.objects.get_or_create(username=response.user.email)
                auth_login(request, django_user)

                # Redirect to home view where the role check happens
                return redirect('home')
        
        except Exception as e:
            messages.error(request, f"Login failed: {e}")
    
    return render(request, 'accounts/login.html')


@login_required
def home_view(request):
    # Retrieve the stored user data from the session
    user_data = request.session.get('user')

    # Debugging: Print user data to the console
    print("User Data in home_view:", user_data)

    if user_data:
        # Validate the user's role based on the 'is_admin' flag
        if user_data['user_metadata'].get('is_admin'):
            print("Redirecting to admin_dashboard")
            return redirect('admin_dashboard')
        else:
            print("Redirecting to user_dashboard")
            return redirect('user_dashboard')
    else:
        messages.error(request, "User data not found. Please log in again.")
        return redirect('login')


@login_required
def admin_dashboard(request):
    # Retrieve the stored user data from the session
    user_data = request.session.get('user')
    
    # Debugging: Print user data to the console
    print("User Data in admin_dashboard:", user_data)

    # Ensure only admins can access this view
    if user_data and user_data['user_metadata'].get('is_admin'):
        return render(request, 'accounts/admin_dashboard.html', {'user_data': user_data})
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def user_dashboard(request):
    # Retrieve the stored user data from the session
    user_data = request.session.get('user')
    
    # Ensure that user_data is defined before using it
    if user_data is None:
        # If user_data is not found in the session, redirect to login
        return redirect('login')

    return render(request, 'accounts/user_dashboard.html', {'user_data': user_data})

