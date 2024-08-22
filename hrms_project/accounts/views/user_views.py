from typing import Dict, Any
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..services.user_service_v1 import UserService
from ..utils.decorators import admin_required
from ..exceptions import UserCreationError, UserUpdateError, UserDeletionError, UserNotFoundException
import logging

logger = logging.getLogger(__name__)

@login_required
@csrf_exempt
@require_POST
def proxy_supabase(request: HttpRequest) -> JsonResponse:
    try:
        user_service = UserService()
        formatted_users = user_service.get_all_users()
        return JsonResponse({'users': formatted_users})
    except Exception as e:
        logger.error(f"Failed to fetch users in proxy_supabase: {str(e)}")
        return JsonResponse({'error': f'Failed to fetch users: {str(e)}'}, status=500)

@login_required
@admin_required
def list_users(request: HttpRequest) -> HttpResponse:
    query: str = request.GET.get('q', '')
    page: str = request.GET.get('page', '1')
    user_service = UserService()
    
    try:
        users = user_service.get_all_users()
        if query:
            query = query.lower()
            users = [user for user in users if query in user['email'].lower()]

        formatted_users = [user_service.format_user(user) for user in users]
        paginator = Paginator(formatted_users, 10)
        try:
            users_page = paginator.page(page)
        except PageNotAnInteger:
            users_page = paginator.page(1)
        except EmptyPage:
            users_page = paginator.page(paginator.num_pages)

        return render(request, 'accounts/list_users.html', {'users': users_page, 'query': query})
    except Exception as e:
        logger.error(f"Error in list_users view: {str(e)}")
        messages.error(request, "An error occurred while fetching users.")
        return redirect('accounts:home')

@login_required
@admin_required
def create_user_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        email: str = request.POST.get('email', '')
        password: str = request.POST.get('password', '')
        first_name: str = request.POST.get('first_name', '')
        last_name: str = request.POST.get('last_name', '')
        is_admin: bool = request.POST.get('is_admin') == 'on'

        # Input validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return render(request, 'accounts/create_user.html')

        if not password or len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'accounts/create_user.html')

        if not first_name or not last_name:
            messages.error(request, "First name and last name are required.")
            return render(request, 'accounts/create_user.html')

        user_service = UserService()
        user_data: Dict[str, Any] = {
            'email': email,
            'password': password,
            'user_metadata': {
                'first_name': first_name,
                'last_name': last_name,
                'is_admin': is_admin
            }
        }

        try:
            user = user_service.create_user(user_data)
            messages.success(request, f"User {email} created successfully.")
        except UserCreationError as e:
            logger.error(f"Error during User creation: {str(e)}")
            messages.error(request, str(e))

        return redirect('accounts:list_users')

    return render(request, 'accounts/create_user.html')

@login_required
@admin_required
def update_user(request: HttpRequest, user_id: str) -> HttpResponse:
    user_service = UserService()
    try:
        user = user_service.get_user_by_id(user_id)
    except UserNotFoundException as e:
        messages.error(request, str(e))
        return redirect('accounts:list_users')

    if request.method == 'POST':
        email: str = request.POST.get('email', '')
        first_name: str = request.POST.get('first_name', '')
        last_name: str = request.POST.get('last_name', '')
        is_admin: bool = request.POST.get('is_admin') == 'on'

        # Input validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email address.")
            return render(request, 'accounts/update_user.html', {'user': user})

        if not first_name or not last_name:
            messages.error(request, "First name and last name are required.")
            return render(request, 'accounts/update_user.html', {'user': user})

        updated_data: Dict[str, Any] = {
            'email': email,
            'user_metadata': {
                'first_name': first_name,
                'last_name': last_name,
                'is_admin': is_admin
            }
        }
        try:
            updated_user = user_service.update_user(user_id, updated_data)
            messages.success(request, "User updated successfully.")
            return redirect('accounts:list_users')
        except UserUpdateError as e:
            messages.error(request, f"Failed to update user: {str(e)}")
    
    return render(request, 'accounts/update_user.html', {'user': user})

@login_required
@admin_required
@require_http_methods(["DELETE"])
def delete_user(request: HttpRequest, user_id: str) -> JsonResponse:
    user_service = UserService()
    try:
        success = user_service.delete_user(user_id)
        if success:
            return JsonResponse({"success": True, "message": "User deleted successfully"})
        else:
            return JsonResponse({"success": False, "message": "Failed to delete user. User may not exist."}, status=404)
    except UserDeletionError as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        return JsonResponse({"success": False, "message": str(e)}, status=500)