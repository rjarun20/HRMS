import os
import requests
import logging
from django.core.cache import cache
from dotenv import load_dotenv
from ..utils.decorators import admin_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from ..exceptions import UserCreationError, UserUpdateError, UserDeletionError
from ..supabase_client import supabase


# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_role_key = os.getenv('SUPABASE_KEY')
        if not self.supabase_url or not self.service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        self.headers = {
            'apikey': self.service_role_key,
            'Authorization': f'Bearer {self.service_role_key}'
        }

    def get_all_users(self):
        cached_users = cache.get('all_users')
        if cached_users is not None:
            logger.info("Returning users from cache")
            return cached_users

        try:
            response = requests.get(f"{self.supabase_url}/auth/v1/admin/users", headers=self.headers)
            response.raise_for_status()
            users = response.json()
            
            if not isinstance(users, list):
                users = users.get('users', [])
            
            cache.set('all_users', users, 300)
            
            logger.info(f"Fetched {len(users)} users from Supabase and cached")
            return users
        except requests.RequestException as e:
            logger.error(f"Error fetching all users: {str(e)}")
            raise

    def get_user_by_id(self, user_id):
        try:
            response = requests.get(f"{self.supabase_url}/auth/v1/admin/users/{user_id}", headers=self.headers)
            response.raise_for_status()
            user_data = response.json()
            return self.format_user(user_data)
        except requests.RequestException as e:
            logger.error(f"Error fetching user {user_id}: {str(e)}")
            raise

    def create_user(self, user_data):
        try:
            response = supabase.auth.sign_up({
                "email": user_data['email'],
                "password": user_data['password'],
                "options": {
                    "data": {
                        "first_name": user_data['user_metadata']['first_name'],
                        "last_name": user_data['user_metadata']['last_name'],
                        "is_admin": user_data['user_metadata']['is_admin']
                    }
                }
            })
            
            if response.user is None:
                raise UserCreationError(f"Failed to create user with email {user_data['email']}")
            
            self.invalidate_user_cache()
            return response.user
        except Exception as e:
            if "User already registered" in str(e):
                raise UserCreationError(f"User with email {user_data['email']} already exists.")
            raise UserCreationError(f"Error creating user: {str(e)}")
        

    def update_user(self, user_id, updated_data):
        try:
            response = requests.put(f"{self.supabase_url}/auth/v1/admin/users/{user_id}", 
                                    headers=self.headers, json=updated_data)
            response.raise_for_status()
            self.invalidate_user_cache()
            return self.format_user(response.json())
        except requests.RequestException as e:
            raise UserUpdateError(f"Error updating user {user_id}: {str(e)}")

    def delete_user(self, user_id):
        try:
            response = requests.delete(
                f"{self.supabase_url}/auth/v1/admin/users/{user_id}",
                headers=self.headers
            )
            if response.status_code == 404:
                raise UserDeletionError(f"User with ID {user_id} not found.")
            response.raise_for_status()
            self.invalidate_user_cache()
            return True
        except requests.RequestException as e:
            raise UserDeletionError(f"Error deleting user {user_id}: {str(e)}")
        
    def update_current_user(self, user_id, updated_data):
        try:
            user_headers = {
                'apikey': self.service_role_key,
                'Authorization': f'Bearer {updated_data.get("access_token")}'
            }
            response = requests.put(f"{self.supabase_url}/auth/v1/user", 
                                    headers=user_headers, json=updated_data)
            response.raise_for_status()
            self.invalidate_user_cache()
            logger.info(f"Current user updated: {user_id}")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error updating current user {user_id}: {str(e)}")
            raise

    def format_user(self, user):
        if isinstance(user, str):
            user_data = self.get_user_by_id(user)
        else:
            user_data = user

        return {
            'id': user_data.get('id'),
            'email': user_data.get('email'),
            'is_admin': user_data.get('user_metadata', {}).get('is_admin', False),
            'first_name': user_data.get('user_metadata', {}).get('first_name', ''),
            'last_name': user_data.get('user_metadata', {}).get('last_name', ''),
            'created_at': user_data.get('created_at'),
            'last_sign_in_at': user_data.get('last_sign_in_at'),
            'email_confirmed': bool(user_data.get('email_confirmed_at'))
        }

    def invalidate_user_cache(self):
        cache.delete('all_users')
        logger.info("User cache invalidated")