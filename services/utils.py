from django.core.mail import send_mail
from django.conf import settings
from .models import AttemptMailing


def send_mailing_manually(mailing):
    """
    Ручная отправка рассылки
    Возвращает кортеж (успешно_отправлено, ошибки)
    """
    from django.utils import timezone

    # Проверка времени
    now = timezone.now()
    if now < mailing.start_datetime:
        return False, "Рассылка еще не началась"

    if now > mailing.end_datetime:
        return False, "Время рассылки уже прошло"

    if mailing.status != mailing.Status.STARTED:
        mailing.update_status()
        if mailing.status != mailing.Status.STARTED:
            return False, f"Статус рассылки: {mailing.get_status_display()}"

    # Отправка
    results = mailing.send_to_all_recipients()

    if results['success'] > 0:
        return True, f"Успешно отправлено: {results['success']}, Ошибок: {results['failed']}"
    else:
        return False, "Не удалось отправить ни одного письма"