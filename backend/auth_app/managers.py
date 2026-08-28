from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Create users whose unique login identifier is their email address."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with an email address."""
        if not email:
            raise ValueError("Eine E-Mail-Adresse ist erforderlich.")

        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with administrative permissions."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Ein Superuser muss is_staff=True besitzen.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Ein Superuser muss is_superuser=True besitzen.")

        return self.create_user(email, password, **extra_fields)
