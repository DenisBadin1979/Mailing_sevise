from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import EmailVerification, PasswordResetToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "email_verified",
    )
    list_filter = ("is_staff", "is_active", "email_verified")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Персональная информация",
            {"fields": ("first_name", "last_name", "phone", "company")},
        ),
        (
            "Права доступа",
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
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
        ("Верификация", {"fields": ("email_verified",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "expires_at", "is_used")
    list_filter = ("is_used", "created_at")
    search_fields = ("user__email", "token")


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "expires_at", "is_used")
    list_filter = ("is_used", "created_at")
    search_fields = ("user__email", "token")
