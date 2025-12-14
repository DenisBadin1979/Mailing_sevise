from django.core.cache import cache

from .models import Mailing


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

    if results["success"] > 0:
        return (
            True,
            f"Успешно отправлено: {results['success']}, Ошибок: {results['failed']}",
        )
    else:
        return False, "Не удалось отправить ни одного письма"


def get_cached_mailing_stats(user):
    """Получаем статистику из кеша или вычисляем"""
    cache_key = f"mailing_stats_{user.id}"
    stats = cache.get(cache_key)

    if not stats:
        # Вычисляем статистику
        stats = {
            "total_mailings": Mailing.objects.filter(owner=user).count(),
            "active_mailings": Mailing.objects.filter(
                owner=user, status="started"
            ).count(),
            # ... другие вычисления
        }
        # Сохраняем в кеш на 5 минут
        cache.set(cache_key, stats, 60 * 5)

    return stats
