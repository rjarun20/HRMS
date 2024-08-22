import os
from typing import Dict, List, Any, Optional
import requests
import logging
from django.core.cache import cache
from dotenv import load_dotenv
from ..exceptions import UserCreationError, UserUpdateError, UserDeletionError, UserNotFoundException
from ..supabase_client import supabase

load_dotenv()

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.supabase_url: str = os.getenv('SUPABASE_URL', '')
        self.service_role_key: str = os.getenv('SUPABASE_KEY', '')
        if not self.supabase_url or not self.service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        self.headers: Dict[str, str] = {
            'apikey': self.service_role_key,
            'Authorization': f'Bearer {self.service_role_key}'
        }

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Retrieve all users from cache or Supabase.

        Returns:
            List[Dict[str, Any]]: A list of user dictionaries.

        Raises:
            requests.RequestException: If there's an error fetching users from Supabase.
        """
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
            
            formatted_users = [self.format_user(user) for user in users]
            cache.set('all_users', formatted_users, 300)
            
            logger.info(f"Fetched {len(formatted_users)} users from Supabase and cached")
            return formatted_users
        except requests.RequestException as e:
            logger.error(f"Error fetching all users: {str(e)}")
            raise

    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve a user by their ID.

        Args:
            user_id (str): The ID of the user to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the user's information.

        Raises:
            UserNotFoundException: If the user is not found.
            requests.RequestException: If there's an error fetching the user from Supabase.
        """
        try:
            response = requests.get(f"{self.supabase_url}/auth/v1/admin/users/{user_id}", headers=self.headers)
            if response.status_code == 404:
                raise UserNotFoundException(f"User with ID {user_id} not found.")
            response.raise_for_status()
            user_data = response.json()
            return self.format_user(user_data)
        except requests.RequestException as e:
            logger.error(f"Error fetching user {user_id}: {str(e)}")
            raise

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user in Supabase.

        Args:
            user_data (Dict[str, Any]): A dictionary containing the user's information.

        Returns:
            Dict[str, Any]: A dictionary containing the created user's information.

        Raises:
            UserCreationError: If there's an error creating the user.
        """
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
            return self.format_user(response.user)
        except Exception as e:
            if "User already registered" in str(e):
                raise UserCreationError(f"User with email {user_data['email']} already exists.")
            raise UserCreationError(f"Error creating user: {str(e)}")

    def update_user(self, user_id: str, updated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a user's information in Supabase.

        Args:
            user_id (str): The ID of the user to update.
            updated_data (Dict[str, Any]): A dictionary containing the updated user information.

        Returns:
            Dict[str, Any]: A dictionary containing the updated user's information.

        Raises:
            UserUpdateError: If there's an error updating the user.
        """
        try:
            response = requests.put(f"{self.supabase_url}/auth/v1/admin/users/{user_id}", 
                                    headers=self.headers, json=updated_data)
            if response.status_code == 404:
                raise UserUpdateError(f"User with ID {user_id} not found.")
            response.raise_for_status()
            self.invalidate_user_cache()
            return self.format_user(response.json())
        except requests.RequestException as e:
            raise UserUpdateError(f"Error updating user {user_id}: {str(e)}")

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from Supabase.

        Args:
            user_id (str): The ID of the user to delete.

        Returns:
            bool: True if the user was successfully deleted.

        Raises:
            UserDeletionError: If there's an error deleting the user.
        """
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

    def refresh_user_cache(self) -> None:
        """
        Refresh the user cache by fetching all users from Supabase and updating the cache.
        """
        try:
            self.get_all_users()  # This method already handles caching
            logger.info("User cache refreshed")
        except requests.RequestException as e:
            logger.error(f"Error refreshing user cache: {str(e)}")
            raise

    def format_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format user data into a consistent structure.

        Args:
            user (Dict[str, Any]): The user data to format.

        Returns:
            Dict[str, Any]: A dictionary containing the formatted user information.
        """
        return {
            'id': user.get('id'),
            'email': user.get('email'),
            'is_admin': user.get('user_metadata', {}).get('is_admin', False),
            'first_name': user.get('user_metadata', {}).get('first_name', ''),
            'last_name': user.get('user_metadata', {}).get('last_name', ''),
            'created_at': user.get('created_at'),
            'last_sign_in_at': user.get('last_sign_in_at'),
            'email_confirmed': bool(user.get('email_confirmed_at'))
        }

    def invalidate_user_cache(self) -> None:
        """
        Invalidate the user cache.
        """
        cache.delete('all_users')
        logger.info("User cache invalidated")