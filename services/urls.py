from services.apps import ServicesConfig
from django.urls import path
from services.views import BaseView, MailingListView

app_name = ServicesConfig.name


urlpatterns = [

    path("", BaseView.as_view(), name="index"),
    path('',  MailingListView.as_view(), name='mailing'),
]
