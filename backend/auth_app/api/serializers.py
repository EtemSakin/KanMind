"""Serializers for authentication and user data."""

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


User = get_user_model()


class UserShortSerializer(serializers.ModelSerializer):
    """Serialize public user information."""

    class Meta:
        model = User
        fields = ("id", "email", "fullname")
        read_only_fields = fields


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate and create new user accounts."""

    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("fullname", "email", "password", "repeated_password")

    def validate_email(self, value):
        """Normalize the email address and ensure that it is unique."""
        email = User.objects.normalize_email(value).lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "Ein Benutzer mit dieser E-Mail-Adresse existiert bereits."
            )
        return email

    def validate(self, attrs):
        """Validate matching passwords and Django password requirements."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Die Passwörter stimmen nicht überein."}
            )

        candidate = User(email=attrs["email"], fullname=attrs["fullname"])
        try:
            validate_password(attrs["password"], user=candidate)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {"password": list(error.messages)}
            ) from error

        return attrs

    def create(self, validated_data):
        """Create a user from validated registration data."""
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    """Validate user login credentials."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the supplied email address and password."""
        email = User.objects.normalize_email(attrs["email"]).lower()
        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=attrs["password"],
        )

        if user is None:
            raise serializers.ValidationError(
                "E-Mail-Adresse oder Passwort ist ungültig."
            )

        attrs["user"] = user
        return attrs
