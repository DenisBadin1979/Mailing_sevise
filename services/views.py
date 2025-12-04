from datetime import timezone
from winreg import CreateKeyEx

from django.urls import reverse_lazy
from django.utils import timezone

from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from services.models import Mailing, RecipientMailing, Message


class BaseView(TemplateView):
    template_name = "services/base.html"


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