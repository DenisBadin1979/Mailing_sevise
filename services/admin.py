from django.contrib import admin
from .models import RecipientMailing, Message, Mailing

@admin.register(RecipientMailing)
class RecipientMailingAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'email')
    list_filter = ('last_name',)
    search_fields = ('last_name', 'first_name', 'middle_name', 'email')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject_message', 'body_message')
    search_fields = ('subject_message', 'body_message')


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'start_datetime', 'end_datetime', 'status')
    list_filter = ('status', 'start_datetime')
    filter_horizontal = ('recipients',)
    readonly_fields = ('created_at', 'updated_at')