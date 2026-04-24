from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import NotAuthenticated

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Call the original authenticate method
        print("ddddddddddd",request)
        user_auth_tuple = super().authenticate(request)
        print("userrrrrrr",user_auth_tuple)
        if user_auth_tuple is None:
            # Raise a custom error instead of default
            raise NotAuthenticated(detail="Please login")
        
        print("aaaaaaaaa")
        return user_auth_tuple