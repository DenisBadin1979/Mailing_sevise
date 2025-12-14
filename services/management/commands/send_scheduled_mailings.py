import logging

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from services.models import Mailing

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Отправка всех рассылок, которые должны быть отправлены сейчас"

    def handle(self, *args, **options):
        now = timezone.now()

        # Находим рассылки для отправки
        mailings = Mailing.objects.filter(
            is_active=True,
            start_datetime__lte=now,
            end_datetime__gte=now,
            status="started",
        )

        self.stdout.write(f"Найдено {mailings.count()} рассылок для отправки")

        for mailing in mailings:
            self.stdout.write(f"Обработка рассылки #{mailing.id}...")

            # Отправляем каждому получателю
            for recipient in mailing.recipients.all():
                try:
                    send_mail(
                        subject=mailing.message.subject_message,
                        message=mailing.message.body_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )

                    # Записываем успешную попытку
                    mailing.attempts.create(
                        recipient=recipient,
                        status="success",
                        server_response="Письмо успешно отправлено",
                    )

                    self.stdout.write(
                        self.style.SUCCESS(f"  ✓ Отправлено {recipient.email}")
                    )

                except Exception as e:
                    # Записываем неудачную попытку
                    mailing.attempts.create(
                        recipient=recipient, status="failed", server_response=str(e)
                    )

                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Ошибка {recipient.email}: {e}")
                    )

        self.stdout.write(self.style.SUCCESS("Отправка завершена"))
