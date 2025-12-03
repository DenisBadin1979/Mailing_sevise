from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView

from services.models import Mailing, RecipientMailing


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

        # Добавляем статистику
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='started').count()
        context['unique_recipients'] = RecipientMailing.objects.count()

        return context

class RecipientMailingDetailVew(DetailView):
    template_name = "services/rec.html"
    model = RecipientMailing
    context_object_name = 'recipient'