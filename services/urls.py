from services.apps import ServicesConfig
from django.urls import path
from services.views import BaseView, MailingListView, RecipientMailingListVew, RecipientMailingCreateView, \
    RecipientMailingDetailView, RecipientMailingUpdateView, RecipientMailingDeleteView, MessageDeleteView, \
    MessageUpdateView, MessageDetailView, MessageCreateView, MessageListVew, MailingCreateView, MailingUpdateView, \
    MailingDetailView, MailingDeleteView
from . import views
app_name = ServicesConfig.name


urlpatterns = [

    path("home/", BaseView.as_view(), name="index"),
    path('',  MailingListView.as_view(), name='mailing_list'),
    path('recipient/',  RecipientMailingListVew.as_view(), name='recipient_list'),
    path('recipient_create/',  RecipientMailingCreateView.as_view(), name='recipient_create'),
    path('recipient/<int:pk>/',  RecipientMailingDetailView.as_view(), name='recipient_detail'),
    path('recipient/<int:pk>/edit/',  RecipientMailingUpdateView.as_view(), name='recipient_edit'),
    path('recipient/<int:pk>/delete/',  RecipientMailingDeleteView.as_view(), name='recipient_delete'),

    path('message/',  MessageListVew.as_view(), name='message_list'),
    path('message_create/',  MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/',  MessageDetailView.as_view(), name='message_detail'),
    path('message/<int:pk>/edit/',  MessageUpdateView.as_view(), name='message_edit'),
    path('message/<int:pk>/delete/',  MessageDeleteView.as_view(), name='message_delete'),

    path('mail_create/', MailingCreateView.as_view(), name='mail_create'),
    path('mail/<int:pk>/edit/', MailingUpdateView.as_view(), name='mail_edit'),
    path('mail/<int:pk>/',  MailingDetailView.as_view(), name='mail_detail'),
    path('mail/<int:pk>/start/', views.start_mailing_now, name='start_mailing_now'),
    path('mail/<int:pk>/delete/',  MailingDeleteView.as_view(), name='mail_delete'),
]
