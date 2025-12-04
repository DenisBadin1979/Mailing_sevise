
from django.utils import timezone

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

class AttemptMailing (models.Model):
    """Модель попытки рассылки"""
    pass




