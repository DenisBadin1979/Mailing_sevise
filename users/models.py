from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Кастомный менеджер для модели User"""

    def create_user(self, email, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not email:
            raise ValueError("Email обязателен")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя"""

    # Убираем поле username, используем email вместо него
    username = None
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("Пользователь с таким email уже существует."),
        },
    )

    # Дополнительные поля
    phone = models.CharField(_("phone number"), max_length=20, blank=True, null=True)
    email_verified = models.BooleanField(
        _("email verified"),
        default=False,
        help_text=_("Подтвержден ли email пользователя"),
    )

    company = models.CharField(_("company"), max_length=100, blank=True, null=True)

    # Настройки модели
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Полное имя пользователя"""
        return f"{self.last_name} {self.first_name}".strip()

    def get_short_name(self):
        """Короткое имя пользователя"""
        return self.first_name

    @property
    def is_email_verified(self):
        """Проверка, подтвержден ли email"""
        return self.email_verified


class EmailVerification(models.Model):
    """Модель для подтверждения email"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="email_verifications"
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("email verification")
        verbose_name_plural = _("email verifications")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Verification for {self.user.email}"

    def is_valid(self):
        """Проверка валидности токена"""
        return not self.is_used and timezone.now() <= self.expires_at


class PasswordResetToken(models.Model):
    """Модель для сброса пароля"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_reset_tokens"
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("password reset token")
        verbose_name_plural = _("password reset tokens")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Password reset for {self.user.email}"

    def is_valid(self):
        """Проверка валидности токена"""
        return not self.is_used and timezone.now() <= self.expires_at
