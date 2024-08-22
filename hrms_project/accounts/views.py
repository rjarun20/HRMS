from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import requests
import os
import json
import logging
from supabase.lib.client_options import ClientOptions

logger = logging.getLogger(__name__)

from .supabase_client import supabase


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "You must provide both an email and a password.")
            return render(request, 'accounts/login.html')
        
        try:
            response = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            
            if response.user is None:
                messages.error(request, "Login failed: Invalid login credentials.")
            else:
                request.session['user'] = {
                    'id': response.user.id,
                    'email': response.user.email,
                    'role': response.user.role,
                    'app_metadata': response.user.app_metadata,
                    'user_metadata': response.user.user_metadata,
                }
                request.session['access_token'] = response.session.access_token

                messages.success(request, f"Welcome back, {response.user.email}!")
                django_user, created = User.objects.get_or_create(username=response.user.email)
                auth_login(request, django_user)
                return redirect('home')
        
        except Exception as e:
            messages.error(request, f"Login failed: {e}")
    
    return render(request, 'accounts/login.html')


@login_required
def home_view(request):
    user_data = request.session.get('user')

    if user_data:
        if user_data['user_metadata'].get('is_admin'):
            return redirect('admin_dashboard')
        else:
            return redirect('user_dashboard')
    else:
        messages.error(request, "User data not found. Please log in again.")
        return redirect('login')


@login_required
def admin_dashboard(request):
    user_data = request.session.get('user')

    if user_data and user_data['user_metadata'].get('is_admin'):
        return render(request, 'accounts/admin_dashboard.html', {'user_data': user_data})
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')


@login_required
def user_dashboard(request):
    user_data = request.session.get('user')
    
    if user_data is None:
        return redirect('login')

    return render(request, 'accounts/user_dashboard.html', {'user_data': user_data})


@login_required
def create_user_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        is_admin = request.POST.get('is_admin') == 'on'

        try:
            print(f"Attempting to sign up user with email: {email}")
            
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "is_admin": is_admin
                    }
                }
            })

            # print(f"Supabase response: {response}")  # Debug print

            if response.user:
                logger.info(f"User signed up successfully: {email}")
                messages.success(request, f"User {email} signed up successfully.")
            else:
                logger.error(f"User sign-up failed for email: {email}")
                messages.error(request, "User sign-up failed.")

        except Exception as e:
            logger.exception(f"Error signing up user: {email}")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            messages.error(request, f"User sign-up failed: {str(e)}")

        return redirect('list_users')

    return render(request, 'accounts/create_user.html')

def logout_view(request):
    try:
        supabase.auth.sign_out()
        messages.success(request, "You have been logged out successfully.")
    except Exception as e:
        messages.error(request, f"Logout failed: {e}")

    django_logout(request)
    return redirect('login')


@login_required
def list_users(request):
    return render(request, 'accounts/list_users.html')


@login_required
@csrf_exempt
@require_POST
def proxy_supabase(request):
    print("Proxy Supabase endpoint reached.")
    supabase_url = os.environ.get('SUPABASE_URL')
    service_role_key = os.environ.get('SUPABASE_KEY')

    if not supabase_url or not service_role_key:
        return JsonResponse({'error': 'Supabase credentials are missing'}, status=500)
    
    headers = {
        'apikey': service_role_key,
        'Authorization': f'Bearer {service_role_key}'
    }
    
    try:
        response = requests.get(f"{supabase_url}/auth/v1/admin/users", headers=headers)
        response.raise_for_status()
        
        users_data = response.json()
        
        # Process the users data
        formatted_users = []
        for user in users_data.get('users', []):
            formatted_user = {
                'id': user.get('id'),
                'email': user.get('email'),
                'is_admin': user.get('user_metadata', {}).get('is_admin', False),
                'first_name': user.get('user_metadata', {}).get('first_name', ''),
                'last_name': user.get('user_metadata', {}).get('last_name', ''),
                'created_at': user.get('created_at'),
                'last_sign_in_at': user.get('last_sign_in_at'),
                'email_confirmed': bool(user.get('email_confirmed_at'))
            }
            formatted_users.append(formatted_user)
        
        print(f"Processed {len(formatted_users)} users")
        return JsonResponse({'users': formatted_users})
    
    except requests.RequestException as e:
        print(f"Error fetching users: {str(e)}")
        return JsonResponse({'error': f'Failed to fetch users: {str(e)}'}, status=500)

# Additional views for employee management and leave management...

@login_required
def add_employee(request):
    return render(request, 'accounts/add_employee.html')

@login_required
def list_employees(request):
    employees = []  # Replace with actual query to fetch employees
    return render(request, 'accounts/list_employees.html', {'employees': employees})

@login_required
def approve_leaves(request):
    leave_requests = []  # Replace with actual query to fetch leave requests
    return render(request, 'accounts/approve_leaves.html', {'leave_requests': leave_requests})

@login_required
def leave_reports(request):
    reports = []  # Replace with actual logic to generate reports
    return render(request, 'accounts/leave_reports.html', {'reports': reports})

@login_required
def pending_kyc(request):
    pending_applications = []  # Replace with actual logic to get pending KYC applications
    return render(request, 'accounts/pending_kyc.html', {'pending_applications': pending_applications})

@login_required
def kyc_reports(request):
    kyc_report_data = []  # Replace with actual logic to get KYC report data
    return render(request, 'accounts/kyc_reports.html', {'kyc_report_data': kyc_report_data})