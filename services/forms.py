# forms.py
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Mailing


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_datetime', 'end_datetime', 'status', 'message', 'recipients']

        widgets = {
            'start_datetime': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),
            'end_datetime': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Select(attrs={'class': 'form-control'}),
            'recipients': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем формат для полей даты и времени
        for field_name in ['start_datetime', 'end_datetime']:
            if self[field_name].value():
                dt_value = self[field_name].value()
                if isinstance(dt_value, timezone.datetime):
                    self.initial[field_name] = dt_value.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        """Основная валидация формы"""
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')

        # Проверяем, что оба поля заполнены
        if not start_datetime:
            self.add_error('start_datetime', 'Укажите дату и время начала рассылки')

        if not end_datetime:
            self.add_error('end_datetime', 'Укажите дату и время окончания рассылки')

        # Если хотя бы одно поле не заполнено, прекращаем дальнейшую валидацию
        if not start_datetime or not end_datetime:
            return cleaned_data

        now = timezone.now()

        # 1. Проверка: start_datetime не может быть в прошлом
        if start_datetime < now:
            self.add_error('start_datetime', 'Дата и время начала не могут быть в прошлом')

        # 2. Проверка: start_datetime должен быть раньше end_datetime
        if end_datetime <= start_datetime:
            self.add_error('end_datetime', 'Дата окончания должна быть позже даты начала')

        # 3. Проверка: end_datetime не может быть в прошлом (дополнительная проверка)
        if end_datetime < now:
            self.add_error('end_datetime', 'Дата и время окончания не могут быть в прошлом')

        # 4. Дополнительная проверка минимального интервала (например, 5 минут)
        min_duration = timezone.timedelta(minutes=5)
        if (end_datetime - start_datetime) < min_duration:
            self.add_error('end_datetime', 'Интервал между началом и окончанием должен быть не менее 5 минут')

        return cleaned_data