from django.contrib import admin

from .models import AttemptMailing, Mailing, Message, RecipientMailing


@admin.register(RecipientMailing)
class RecipientMailingAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "middle_name", "email")
    list_filter = ("last_name",)
    search_fields = ("last_name", "first_name", "middle_name", "email")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject_message", "body_message")
    search_fields = ("subject_message", "body_message")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "start_datetime", "end_datetime", "status")
    list_filter = ("status", "start_datetime")
    filter_horizontal = ("recipients",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(AttemptMailing)
class AttemptMailingAdmin(admin.ModelAdmin):
    list_display = (
        "attempt_time",
        "status",
        "server_response",
        "mailing",
        "recipients",
    )
    list_filter = ("attempt_time", "status", "server_response")
    search_fields = ("attempt_time", "status")
