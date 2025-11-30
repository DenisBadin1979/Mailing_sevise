from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from services.models import Mailing, RecipientMailing


class BaseView(TemplateView):
    template_name = "services/base.html"


class HomePageView(ListView):
    template_name = 'services/mailing.html'
    model = Mailing
    context_object_name = 'mailings'

    def get_queryset(self):
        # Можно вернуть последние рассылки или пустой queryset
        return Mailing.objects.all()[:5]  # последние 5 рассылок

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Добавляем статистику
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='started').count()
        context['unique_recipients'] = RecipientMailing.objects.count()

        return context