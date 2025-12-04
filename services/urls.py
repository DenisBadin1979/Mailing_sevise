from services.apps import ServicesConfig
from django.urls import path
from services.views import BaseView, MailingListView, RecipientMailingListVew, RecipientMailingCreateView, \
    RecipientMailingDetailView, RecipientMailingUpdateView, RecipientMailingDeleteView

app_name = ServicesConfig.name


urlpatterns = [

    path("home/", BaseView.as_view(), name="index"),
    path('',  MailingListView.as_view(), name='mailing_list'),
    path('recipient/',  RecipientMailingListVew.as_view(), name='recipient_list'),
    path('recipient_create/',  RecipientMailingCreateView.as_view(), name='recipient_create'),
    path('recipient/<int:pk>/',  RecipientMailingDetailView.as_view(), name='recipient_detail'),
    path('recipient/<int:pk>/edit/',  RecipientMailingUpdateView.as_view(), name='recipient_edit'),
    path('recipient/<int:pk>/delete/',  RecipientMailingDeleteView.as_view(), name='recipient_delete'),
]
