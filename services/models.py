from django.db import models

class RecipientMailing (models.Model):
    """Модель получатель рассылки"""
    email = models.EmailField(unique=True, verbose_name='Адрес электронный почты')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=150, verbose_name='Отчество')
    comment = models.TextField()


class Message (models.Model):
    """Модель сообщения"""
    pass

class Mailing (models.Model):
    """Модель рассылка"""
    pass

class AttemptMailing (models.Model):
    """Модель попытки рассылки"""
    pass




