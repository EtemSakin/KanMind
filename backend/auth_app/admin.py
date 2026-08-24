from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from auth_app.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    ordering = ("email",)
    list_display = ("email", "fullname", "is_staff", "is_active")
    search_fields = ("email", "fullname")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Persönliche Daten", {"fields": ("fullname",)}),
        (
            "Berechtigungen",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Wichtige Daten", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "fullname",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
