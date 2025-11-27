from django.db import models

class RecipientMailing (models.Model):
    """Модель получатель рассылки"""
    email = models.EmailField(unique=True, verbose_name='Адрес электронный почты')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    middle_name = models.CharField(max_length=150, blank=True, verbose_name='Отчество')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

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

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-created_at']

    def __str__(self):
        return f"Рассылка #{self.id} - {self.message.subject_message}"

    @property
    def is_active(self):
        """Проверяет, активна ли рассылка в данный момент"""
        from django.utils import timezone
        now = timezone.now()
        return (self.start_datetime <= now <= self.end_datetime and
                self.status == self.Status.STARTED)

class AttemptMailing (models.Model):
    """Модель попытки рассылки"""
    pass




