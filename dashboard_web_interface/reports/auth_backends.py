from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        # Hardcoded admin account for testing
        if email == 'admin@apo.com.tn' and password == 'admin123':
            # Create or get the admin user
            try:
                user = UserModel.objects.get(email=email)
            except UserModel.DoesNotExist:
                # Create the admin user if it doesn't exist
                user = UserModel.objects.create_user(
                    username=email,  # Using email as username
                    email=email,
                    password=password,
                    is_staff=True,
                    is_superuser=True,
                    is_verified=True,
                    is_active=True
                )
            return user

        # For other users, try to authenticate normally
        try:
            user = UserModel.objects.get(email=email)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
        return None 