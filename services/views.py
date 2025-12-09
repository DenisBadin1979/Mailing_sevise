from datetime import timezone
from winreg import CreateKeyEx

from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from services.forms import MailingForm
from services.models import Mailing, RecipientMailing, Message
from services.utils import send_mailing_manually

from django.contrib import messages



class BaseView(TemplateView):
    template_name = "services/base.html"


@login_required
def start_mailing_now(request, pk):
    """Ручной запуск рассылки через интерфейс"""
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверка прав доступа
    # if not (request.user == mailing.owner or
    #         request.user.groups.filter(name='managers').exists()):
    #     messages.error(request, 'У вас нет прав для запуска этой рассылки')
    #     return redirect('mailing_detail', pk=pk)

    # Отправка рассылки
    success, message = send_mailing_manually(mailing)

    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect('mail_detail', pk=pk)

class MailingListView(ListView):
    template_name = 'services/mailing_list.html'
    model = Mailing
    context_object_name = 'mailings_list'

    def get_queryset(self):
        # Возвращаем последние рассылки для отображения
        return Mailing.objects.all()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # Добавляем статистику
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='started',
                                                            start_datetime__lte=now,
                                                            end_datetime__gte=now).count()
        context['unique_recipients'] = RecipientMailing.objects.count()

        return context

class RecipientMailingListVew(ListView):
    template_name = "services/recipient_list.html"
    model = RecipientMailing
    context_object_name = 'recipients'
    success_url = reverse_lazy('mailings_list')


class RecipientMailingCreateView(CreateView):
    template_name = "services/recipient_create.html"
    model = RecipientMailing
    fields = ['email', 'last_name', 'first_name', 'middle_name', 'comment']
    success_url = reverse_lazy('services:recipient_list')

class RecipientMailingDetailView(DetailView):
    template_name = "services/recipient_detail.html"
    model = RecipientMailing
    context_object_name = 'recipient_detail'
    success_url = reverse_lazy('recipient_list')

class RecipientMailingUpdateView(UpdateView):
    template_name = "services/recipient_create.html"
    model = RecipientMailing
    fields = ['email', 'last_name', 'first_name', 'middle_name', 'comment']
    success_url = reverse_lazy('services:recipient_list')


class RecipientMailingDeleteView(DeleteView):
    model = RecipientMailing
    template_name = 'services/recipient_delete.html'
    context_object_name = 'recipient_delete'
    success_url = reverse_lazy('services:recipient_list')

class MessageListVew(ListView):
    template_name = "services/message_list.html"
    model = Message
    context_object_name = 'messages'
    success_url = reverse_lazy('messages_list')


class MessageCreateView(CreateView):
    template_name = "services/message_create.html"
    model = Message
    fields = ['subject_message', 'body_message']
    success_url = reverse_lazy('services:message_list')

class MessageDetailView(DetailView):
    template_name = "services/message_detail.html"
    model = Message
    context_object_name = 'message_detail'
    success_url = reverse_lazy('message_list')

class MessageUpdateView(UpdateView):
    template_name = "services/message_create.html"
    model = Message
    fields = ['subject_message', 'body_message']
    success_url = reverse_lazy('services:message_list')


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'services/message_delete.html'
    context_object_name = 'message_delete'
    success_url = reverse_lazy('services:message_list')

class MailingCreateView(CreateView):
    template_name = "services/mail_create.html"
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('services:mailing_list')

class MailingDetailView(DetailView):
    template_name = "services/mail_detail.html"
    model = Mailing
    context_object_name = 'mail_detail'
    success_url = reverse_lazy('services:mailing_list')

    def get_object(self, queryset=None):
        """Получаем объект и обновляем его статус"""
        obj = super().get_object(queryset)
        obj.update_status()  # ← пересчёт и сохранение статуса
        return obj

    def get_context_data(self, **kwargs):
        """Добавляем в контекст информацию о текущем статусе"""
        context = super().get_context_data(**kwargs)
        mailing = self.get_object()
        context['current_status'] = mailing.get_current_status()
        context['status_changed'] = (mailing.status != context['current_status'])

        # Добавляем информацию о возможности отправки
        context['can_send_now'] = mailing.can_send_now()

        # Статистика попыток
        attempts = mailing.attempts.all()
        context['attempts'] = attempts
        context['success_count'] = attempts.filter(status='success').count()
        context['failed_count'] = attempts.filter(status='failed').count()

        return context


class MailingUpdateView(UpdateView):
    template_name = "services/mail_create.html"
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('services:mailing_list')


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'services/mail_delete.html'
    context_object_name = 'mail_delete'
    success_url = reverse_lazy('services:mailing_list')