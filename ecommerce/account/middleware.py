# yourapp/middleware.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

@api_view(["POST"])
def refresh_token_view(request):
    refresh_token = request.COOKIES.get("refresh_token")

    if not refresh_token:
        return Response({"error": "No refresh token"}, status=401)

    try:
        refresh = RefreshToken(refresh_token)
        new_access = refresh.access_token
        response = Response({"message": "Token refreshed"})

        response.set_cookie(
            "access_token",
            str(new_access),
            httponly=True,
            secure=True,
            samesite="Lax"
        )

        response.set_cookie(
            "refresh_token",
            str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax"
        )

        return response

    except TokenError:
        return Response({"error": "Invalid refresh token"}, status=401)

        

        
