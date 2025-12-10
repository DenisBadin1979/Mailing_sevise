from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.db import models

from config import settings
from django.contrib.auth import get_user_model
User = get_user_model()

class RecipientMailing (models.Model):
    """Модель получатель рассылки"""
    email = models.EmailField(unique=True, verbose_name='Адрес электронный почты')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    middle_name = models.CharField(max_length=150, blank=True, verbose_name='Отчество')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipients', verbose_name='Владелец')

    class Meta:
        verbose_name = ('Получатель рассылки')
        verbose_name_plural = ('Получатели рассылки')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'




class Message (models.Model):
    """Модель сообщения"""
    subject_message = models.CharField(max_length=100, verbose_name='Тема письма')
    body_message = models.TextField(verbose_name='Тело сообщения')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages', verbose_name='Сообщение')

    class Meta:
        verbose_name = ('Сообщение')
        verbose_name_plural = ('Сообщения')
        ordering = ['subject_message']

    def __str__(self):
        return f'{self.subject_message}'

class Mailing(models.Model):
    """Модель рассылки"""
    class Status(models.TextChoices):
        COMPLETED = 'completed', ('Завершена')
        CREATED = 'created', ('Создана')
        STARTED = 'started', ('Запущена')

    start_datetime = models.DateTimeField(verbose_name='Дата и время первой отправки')
    end_datetime = models.DateTimeField(verbose_name='Дата и время окончания отправки')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
        verbose_name='Статус'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Сообщение'
    )
    recipients = models.ManyToManyField(
        RecipientMailing,
        related_name='mailings',
        verbose_name='Получатели'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='information', verbose_name='Рассылка')

    # ДОБАВЛЯЕМ ЭТО ПОЛЕ:
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-created_at']

    def __str__(self):
        return f"Рассылка #{self.id} - {self.message.subject_message}"

    def update_status(self):
        """
        Динамическое обновление статуса рассылки.
        Вызывается при каждом обращении к объекту рассылки.
        """
        now = timezone.now()

        # Вычисляем новый статус на основе текущего времени
        if now < self.start_datetime:
            new_status = self.Status.CREATED
        elif self.start_datetime <= now <= self.end_datetime:
            new_status = self.Status.STARTED
        else:  # now > self.end_datetime
            new_status = self.Status.COMPLETED

        # Обновляем статус только если он изменился
        if self.status != new_status:
            self.status = new_status
            # Используем update() для избежания рекурсии и вызова save()
            Mailing.objects.filter(pk=self.pk).update(status=new_status)
            # Обновляем объект в памяти
            self.refresh_from_db(fields=['status'])
            return True  # Возвращаем True, если статус был изменен

        return False  # Возвращаем False, если статус не изменился

    def get_current_status(self):
        """
        Возвращает текущий статус без сохранения в БД.
        Используется для отображения статуса без изменения данных.
        """
        now = timezone.now()

        if now < self.start_datetime:
            return self.Status.CREATED
        elif self.start_datetime <= now <= self.end_datetime:
            return self.Status.STARTED
        else:
            return self.Status.COMPLETED

    def save(self, *args, **kwargs):
        """Переопределяем save для валидации"""
        # При сохранении новой рассылки или изменении дат
        # обновляем статус на основе текущего времени
        self.full_clean()

        # Если это новый объект (еще не сохранен в БД)
        if not self.pk:
            now = timezone.now()
            if now < self.start_datetime:
                self.status = self.Status.CREATED
            elif self.start_datetime <= now <= self.end_datetime:
                self.status = self.Status.STARTED
            else:
                self.status = self.Status.COMPLETED
        else:
            # Для существующего объекта пересчитываем статус
            # перед сохранением, если изменились даты
            original = Mailing.objects.get(pk=self.pk)
            if (original.start_datetime != self.start_datetime or
                    original.end_datetime != self.end_datetime):
                now = timezone.now()
                if now < self.start_datetime:
                    self.status = self.Status.CREATED
                elif self.start_datetime <= now <= self.end_datetime:
                    self.status = self.Status.STARTED
                else:
                    self.status = self.Status.COMPLETED

        super().save(*args, **kwargs)

    @property
    def status_display_with_current(self):
        """Отображает как сохраненный статус, так и текущий вычисленный"""
        current = self.get_current_status()
        saved = self.get_status_display()

        if self.status == current:
            return saved
        else:
            return f"{saved} (фактически: {self.Status(current).label})"

    def can_send_now(self):
        """Проверка, можно ли отправлять рассылку сейчас"""
        now = timezone.now()
        return (self.is_active and
                self.start_datetime <= now <= self.end_datetime and
                self.status == self.Status.STARTED)

    def send_to_all_recipients(self):
        """
        Отправка рассылки всем получателям
        Возвращает словарь с результатами
        """
        if not self.can_send_now():
            return {
                'success': 0,
                'failed': 0,
                'errors': ['Рассылка не может быть отправлена в данный момент']
            }

        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }

        for recipient in self.recipients.all():
            try:
                # Отправляем письмо
                send_mail(
                    subject=self.message.subject_message,
                    message=self.message.body_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )

                # Записываем успешную попытку
                AttemptMailing.objects.create(
                    mailing=self,
                    recipient=recipient,
                    status=AttemptMailing.Status.SUCCESS,
                    server_response='Письмо успешно отправлено'
                )

                results['success'] += 1

            except Exception as e:
                # Записываем неудачную попытку
                AttemptMailing.objects.create(
                    mailing=self,
                    recipient=recipient,
                    status=AttemptMailing.Status.FAILED,
                    server_response=str(e)
                )

                results['failed'] += 1
                results['errors'].append(f"{recipient.email}: {str(e)}")

        return results


class AttemptMailing(models.Model):
    """Модель попытки отправки рассылки"""

    class Status(models.TextChoices):
        SUCCESS = 'success', 'Успешно'
        FAILED = 'failed', 'Не успешно'

    attempt_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время попытки'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        verbose_name='Статус'
    )
    server_response = models.TextField(
        blank=True,
        verbose_name='Ответ почтового сервера'
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Рассылка'
    )
    recipients = models.ForeignKey(
        RecipientMailing,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Получатель'
    )


    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
        ordering = ['-attempt_time']

    def __str__(self):
        return f"Попытка #{self.id} - {self.get_status_display()} - {self.attempt_time}"




