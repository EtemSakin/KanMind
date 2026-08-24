from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import User
from auth_app.api.serializers import UserShortSerializer


class UserManagerTests(TestCase):
    def test_create_user_uses_email_as_login(self):
        user = User.objects.create_user(
            email="TEST@Example.com",
            fullname="Test User",
            password="secure-password",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.fullname, "Test User")
        self.assertTrue(user.check_password("secure-password"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_requires_email(self):
        with self.assertRaisesMessage(ValueError, "E-Mail-Adresse"):
            User.objects.create_user(
                email="",
                fullname="Test User",
                password="secure-password",
            )

    def test_create_superuser_sets_required_flags(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            fullname="Admin User",
            password="secure-password",
        )

        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_short_serializer_exposes_only_public_fields(self):
        user = User.objects.create_user(
            email="short@example.com",
            fullname="Short User",
            password="StrongPass-4837!",
        )

        data = UserShortSerializer(user).data

        self.assertEqual(
            data,
            {
                "id": user.id,
                "email": "short@example.com",
                "fullname": "Short User",
            },
        )


class AuthApiTests(APITestCase):
    registration_data = {
        "fullname": "Max Mustermann",
        "email": "max@example.com",
        "password": "StrongPass-4837!",
        "repeated_password": "StrongPass-4837!",
    }

    def test_api_root_is_public(self):
        response = self.client.get(reverse("api-root"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "KanMind API is running.")
        self.assertEqual(response.data["frontend"], "http://127.0.0.1:5500/")

    def test_registration_creates_user_and_returns_frontend_contract(self):
        response = self.client.post(
            reverse("registration"),
            self.registration_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(response.data),
            {"token", "fullname", "email", "user_id"},
        )

        user = User.objects.get(email="max@example.com")
        self.assertTrue(user.check_password("StrongPass-4837!"))
        self.assertEqual(response.data["user_id"], user.id)
        self.assertEqual(response.data["token"], Token.objects.get(user=user).key)

    def test_registration_rejects_different_passwords(self):
        data = {
            **self.registration_data,
            "repeated_password": "DifferentPass-4837!",
        }

        response = self.client.post(reverse("registration"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("repeated_password", response.data)
        self.assertFalse(User.objects.exists())

    def test_registration_rejects_email_case_insensitively(self):
        User.objects.create_user(
            email="max@example.com",
            fullname="Existing User",
            password="StrongPass-4837!",
        )
        data = {**self.registration_data, "email": "MAX@EXAMPLE.COM"}

        response = self.client.post(reverse("registration"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(User.objects.count(), 1)

    def test_login_returns_existing_token_and_frontend_contract(self):
        user = User.objects.create_user(
            email="max@example.com",
            fullname="Max Mustermann",
            password="StrongPass-4837!",
        )
        existing_token = Token.objects.create(user=user)

        response = self.client.post(
            reverse("login"),
            {"email": "MAX@EXAMPLE.COM", "password": "StrongPass-4837!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "token": existing_token.key,
                "fullname": "Max Mustermann",
                "email": "max@example.com",
                "user_id": user.id,
            },
        )

    def test_login_rejects_invalid_credentials(self):
        User.objects.create_user(
            email="max@example.com",
            fullname="Max Mustermann",
            password="StrongPass-4837!",
        )

        response = self.client.post(
            reverse("login"),
            {"email": "max@example.com", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_email_check_requires_authentication(self):
        response = self.client.get(
            reverse("email-check"),
            {"email": "max@example.com"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_email_check_returns_short_user_case_insensitively(self):
        user = User.objects.create_user(
            email="max@example.com",
            fullname="Max Mustermann",
            password="StrongPass-4837!",
        )
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        response = self.client.get(
            reverse("email-check"),
            {"email": "MAX@EXAMPLE.COM"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": user.id,
                "email": "max@example.com",
                "fullname": "Max Mustermann",
            },
        )

    def test_email_check_validates_missing_and_unknown_email(self):
        user = User.objects.create_user(
            email="max@example.com",
            fullname="Max Mustermann",
            password="StrongPass-4837!",
        )
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        missing_response = self.client.get(reverse("email-check"))
        unknown_response = self.client.get(
            reverse("email-check"),
            {"email": "unknown@example.com"},
        )

        self.assertEqual(missing_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", missing_response.data)
        self.assertEqual(unknown_response.status_code, status.HTTP_404_NOT_FOUND)
