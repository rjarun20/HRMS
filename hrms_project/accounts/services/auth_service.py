from ..supabase_client import supabase
from ..exceptions import AuthenticationError

class AuthService:
    @staticmethod
    def login(email, password):
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if response.user is None:
                raise AuthenticationError("Invalid login credentials")
            return {
                'id': response.user.id,
                'email': response.user.email,
                'role': response.user.role,
                'app_metadata': response.user.app_metadata,
                'user_metadata': response.user.user_metadata,
                'access_token': response.session.access_token
            }
        except Exception as e:
            raise AuthenticationError(f"Login failed: {str(e)}")

    @staticmethod
    def logout():
        try:
            supabase.auth.sign_out()
        except Exception as e:
            raise AuthenticationError(f"Logout failed: {str(e)}")