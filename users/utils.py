import secrets
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from .models import User, EmailVerification, PasswordResetToken


def generate_token():
    """Генерация безопасного токена"""
    return secrets.token_urlsafe(32)


def send_verification_email(user, request):
    """Отправка email для подтверждения"""
    # Создаем токен
    token = generate_token()
    expires_at = timezone.now() + timezone.timedelta(hours=24)

    # Сохраняем в базе
    EmailVerification.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )

    # Формируем ссылку
    verification_url = request.build_absolute_uri(
        f'/users/verify-email/{token}/'
    )

    # Отправляем email
    subject = 'Подтверждение email на сервисе рассылок'
    message = render_to_string('users/email_verification.html', {
        'user': user,
        'verification_url': verification_url,
    })

    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=message,
    )


def send_password_reset_email(user, request):
    """Отправка email для сброса пароля"""
    # Создаем токен
    token = generate_token()
    expires_at = timezone.now() + timezone.timedelta(hours=1)

    # Сохраняем в базе
    PasswordResetToken.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )

    # Формируем ссылку
    reset_url = request.build_absolute_uri(
        f'/users/password-reset/{token}/'
    )

    # Отправляем email
    subject = 'Сброс пароля на сервисе рассылок'
    message = render_to_string('users/email/password_reset_confirm.html', {
        'user': user,
        'reset_url': reset_url,
    })

    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=message,
    )


def verify_email_token(token):
    """Верификация email по токену"""
    try:
        verification = EmailVerification.objects.get(
            token=token,
            is_used=False
        )

        if verification.is_valid():
            verification.user.email_verified = True
            verification.user.is_active = True
            verification.user.save()

            verification.is_used = True
            verification.save()

            return verification.user, True
    except EmailVerification.DoesNotExist:
        pass

    return None, False


def verify_password_reset_token(token):
    """Верификация токена сброса пароля"""
    try:
        reset_token = PasswordResetToken.objects.get(
            token=token,
            is_used=False
        )

        if reset_token.is_valid():
            return reset_token.user, True
    except PasswordResetToken.DoesNotExist:
        pass

    return None, False