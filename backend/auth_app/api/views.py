"""Authentication API views for registration, login, and user lookup."""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserShortSerializer,
)


User = get_user_model()


def build_auth_response(user):
    """Return authentication data for the given user."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "fullname": user.fullname,
        "email": user.email,
        "user_id": user.id,
    }


class RegistrationView(APIView):
    """Register new users."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Create a user account and return authentication data."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(build_auth_response(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticate existing users."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate a user and return authentication data."""
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            build_auth_response(serializer.validated_data["user"]),
            status=status.HTTP_200_OK,
        )


class EmailCheckView(APIView):
    """Look up users by email address."""

    def get(self, request):
        """Return public user data for the requested email address."""
        email = request.query_params.get("email", "").strip().lower()
        if not email:
            return Response(
                {"email": ["Dieser Query-Parameter ist erforderlich."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(User, email__iexact=email)
        return Response(UserShortSerializer(user).data)
