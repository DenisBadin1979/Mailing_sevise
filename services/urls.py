from services.apps import ServicesConfig
from django.urls import path
from services.views import BaseView, MailingListView, RecipientMailingDetailVew

app_name = ServicesConfig.name


urlpatterns = [

    path("home/", BaseView.as_view(), name="index"),
    path('',  MailingListView.as_view(), name='mailing_list'),
    path('recipient/<int:pk>/',  RecipientMailingDetailVew.as_view(), name='recipient'),
]
