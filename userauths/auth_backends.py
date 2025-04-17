from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from allauth.account.auth_backends import AuthenticationBackend as AllauthAuthenticationBackend

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # If this is an admin login attempt, use default behavior
        if request and request.path.startswith('/admin/'):
            return super().authenticate(request, username, password, **kwargs)

        user = None
        if '@' in str(username):
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        if user and user.check_password(password):
            # Block superuser from non-admin pages
            if user.is_superuser and request and not request.path.startswith('/admin/'):
                return None
            return user
        return None

class CustomSocialAuthBackend(AllauthAuthenticationBackend):
    def authenticate(self, request, **credentials):
        # First get the user using parent's authenticate method
        user = super().authenticate(request, **credentials)
        
        # If user is a superuser and not accessing admin, deny access
        if user and user.is_superuser and request and not request.path.startswith('/admin/'):
            return None
            
        return user