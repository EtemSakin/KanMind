"""Root view for the KanMind API."""

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class ApiRootView(APIView):
    """Provide basic information about the KanMind API."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        """Return API status information and available endpoints."""
        return Response(
            {
                "message": "KanMind API is running.",
                "frontend": "http://127.0.0.1:5500/",
                "endpoints": {
                    "registration": "/api/registration/",
                    "login": "/api/login/",
                    "email_check": "/api/email-check/?email=...",
                    "boards": "/api/boards/",
                    "tasks": "/api/tasks/",
                },
            }
        )
