import logging

from django.core.management.base import BaseCommand

from services.models import Mailing
from services.utils import send_mailing_manually

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Ручной запуск рассылки по ID"

    def add_arguments(self, parser):
        parser.add_argument(
            "mailing_ids",
            nargs="+",  # один или несколько ID
            type=int,
            help="ID рассылок для отправки",
        )

    def handle(self, *args, **options):
        mailing_ids = options["mailing_ids"]

        for mailing_id in mailing_ids:
            try:
                mailing = Mailing.objects.get(pk=mailing_id)
            except Mailing.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Рассылка с ID {mailing_id} не найдена")
                )
                continue

            self.stdout.write(f"Отправка рассылки ID {mailing_id}...")

            success, message = send_mailing_manually(mailing)

            if success:
                self.stdout.write(self.style.SUCCESS(f"  ✓ {message}"))
            else:
                self.stdout.write(self.style.ERROR(f"  ✗ {message}"))
