from django.contrib.auth.models import AbstractUser
from django.db import models

from auth_app.managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=255)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fullname"]

    objects = UserManager()

    def __str__(self):
        return self.email
