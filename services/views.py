from datetime import timezone

# ВАЖНО: Используем get_user_model вместо прямого импорта
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

User = get_user_model()  # Теперь User - это ваша кастомная модель


from django.contrib import messages

from services.forms import MailingForm
from services.models import Mailing, Message, RecipientMailing
from services.utils import send_mailing_manually


# Миксин для проверки владельца
class OwnerRequiredMixin:
    """Проверяет, является ли пользователь владельцем объекта"""

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user and not request.user.is_staff:
            raise PermissionDenied("Вы не являетесь владельцем этого объекта")
        return super().dispatch(request, *args, **kwargs)


# Миксин для менеджера
class ManagerRequiredMixin(UserPassesTestMixin):
    """Только для менеджеров"""

    def test_func(self):
        return self.request.user.is_staff


# Миксин для пользователя (не менеджера)
class UserRequiredMixin(UserPassesTestMixin):
    """Только для обычных пользователей"""

    def test_func(self):
        return not self.request.user.is_staff


# Миксин для фильтрации по владельцу
class OwnerQuerysetMixin:
    """Фильтрует queryset по владельцу (для пользователей)"""

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return queryset  # Менеджер видит всё
        return queryset.filter(owner=self.request.user)


class BaseView(TemplateView):
    template_name = "services/base.html"

    @method_decorator(cache_page(60 * 10))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


@login_required
def start_mailing_now(request, pk):
    """Ручной запуск рассылки через интерфейс"""
    mailing = get_object_or_404(Mailing, pk=pk)

    # Отправка рассылки
    success, message = send_mailing_manually(mailing)

    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    return redirect("services:mail_detail", pk=pk)


@method_decorator(cache_page(60 * 5), name="dispatch")
class MailingListView(OwnerQuerysetMixin, LoginRequiredMixin, ListView):
    template_name = "services/mailing_list.html"
    model = Mailing
    context_object_name = "mailings_list"

    def get_queryset(self):
        # Возвращаем последние рассылки для отображения
        queryset = super().get_queryset()
        # Дополнительная фильтрация для менеджеров
        if self.request.user.is_staff:
            # Менеджер может фильтровать по пользователям
            user_id = self.request.GET.get("user_id")
            if user_id:
                queryset = queryset.filter(owner_id=user_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # Статистика для пользователя
        if self.request.user.is_staff:
            # Менеджер видит общую статистику
            context["total_mailings"] = Mailing.objects.count()
            context["active_mailings"] = Mailing.objects.filter(
                status="started", start_datetime__lte=now, end_datetime__gte=now
            ).count()
            context["total_users"] = User.objects.count()
        else:
            # Пользователь видит свою статистику
            user_mailings = Mailing.objects.filter(owner=self.request.user)
            context["total_mailings"] = user_mailings.count()
            context["active_mailings"] = user_mailings.filter(
                status="started", start_datetime__lte=now, end_datetime__gte=now
            ).count()

        context["unique_recipients"] = (
            RecipientMailing.objects.filter(owner=self.request.user).count()
            if not self.request.user.is_staff
            else RecipientMailing.objects.count()
        )

        return context

    def get_cache_key(self):
        """Генерируем ключ кеша с учетом пользователя"""
        return f"mailing_list_{self.request.user.id}_{self.request.GET.urlencode()}"


class RecipientMailingListVew(LoginRequiredMixin, UserRequiredMixin, OwnerQuerysetMixin, ListView):
    template_name = "services/recipient_list.html"
    model = RecipientMailing
    context_object_name = "recipients"
    success_url = reverse_lazy("mailings_list")


class RecipientMailingCreateView(LoginRequiredMixin, UserRequiredMixin, CreateView):
    template_name = "services/recipient_create.html"
    model = RecipientMailing
    fields = ["email", "last_name", "first_name", "middle_name", "comment"]
    success_url = reverse_lazy("services:recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user  # Устанавливаем владельца
        return super().form_valid(form)


class RecipientMailingDetailView(LoginRequiredMixin, UserRequiredMixin, DetailView):
    template_name = "services/recipient_detail.html"
    model = RecipientMailing
    context_object_name = "recipient_detail"
    success_url = reverse_lazy("recipient_list")


class RecipientMailingUpdateView(LoginRequiredMixin, UserRequiredMixin, UpdateView):
    template_name = "services/recipient_create.html"
    model = RecipientMailing
    fields = ["email", "last_name", "first_name", "middle_name", "comment"]
    success_url = reverse_lazy("services:recipient_list")


class RecipientMailingDeleteView(LoginRequiredMixin, UserRequiredMixin, DeleteView):
    model = RecipientMailing
    template_name = "services/recipient_delete.html"
    context_object_name = "recipient_delete"
    success_url = reverse_lazy("services:recipient_list")


class MessageListVew(LoginRequiredMixin, UserRequiredMixin, OwnerQuerysetMixin, ListView):
    template_name = "services/message_list.html"
    model = Message
    context_object_name = "messages"
    success_url = reverse_lazy("messages_list")


class MessageCreateView(LoginRequiredMixin, UserRequiredMixin, CreateView):
    template_name = "services/message_create.html"
    model = Message
    fields = ["subject_message", "body_message"]
    success_url = reverse_lazy("services:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user  # Устанавливаем владельца
        return super().form_valid(form)


class MessageDetailView(LoginRequiredMixin, UserRequiredMixin, DetailView):
    template_name = "services/message_detail.html"
    model = Message
    context_object_name = "message_detail"
    success_url = reverse_lazy("message_list")


class MessageUpdateView(LoginRequiredMixin, UserRequiredMixin, UpdateView):
    template_name = "services/message_create.html"
    model = Message
    fields = ["subject_message", "body_message"]
    success_url = reverse_lazy("services:message_list")


class MessageDeleteView(LoginRequiredMixin, UserRequiredMixin, DeleteView):
    model = Message
    template_name = "services/message_delete.html"
    context_object_name = "message_delete"
    success_url = reverse_lazy("services:message_list")


class MailingCreateView(LoginRequiredMixin, UserRequiredMixin, CreateView):
    template_name = "services/mail_create.html"
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("services:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user  # Устанавливаем владельца
        return super().form_valid(form)


class MailingDetailView(LoginRequiredMixin, UserRequiredMixin, DetailView):
    template_name = "services/mail_detail.html"
    model = Mailing
    context_object_name = "mail_detail"
    success_url = reverse_lazy("services:mailing_list")

    def get_object(self, queryset=None):
        """Получаем объект и обновляем его статус"""
        obj = super().get_object(queryset)
        obj.update_status()  # ← пересчёт и сохранение статуса
        return obj

    def get_context_data(self, **kwargs):
        """Добавляем в контекст информацию о текущем статусе"""
        context = super().get_context_data(**kwargs)
        mailing = self.get_object()
        context["current_status"] = mailing.get_current_status()
        context["status_changed"] = mailing.status != context["current_status"]

        # Добавляем информацию о возможности отправки
        context["can_send_now"] = mailing.can_send_now()

        # Статистика попыток
        attempts = mailing.attempts.all()
        context["attempts"] = attempts
        context["success_count"] = attempts.filter(status="success").count()
        context["failed_count"] = attempts.filter(status="failed").count()

        return context


class MailingUpdateView(LoginRequiredMixin, UserRequiredMixin, UpdateView):
    template_name = "services/mail_create.html"
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("services:mailing_list")


class MailingDeleteView(LoginRequiredMixin, UserRequiredMixin, DeleteView):
    model = Mailing
    template_name = "services/mail_delete.html"
    context_object_name = "mail_delete"
    success_url = reverse_lazy("services:mailing_list")


class MailListView(OwnerQuerysetMixin, LoginRequiredMixin, ListView):
    template_name = "services/mail_list.html"
    model = Mailing
    context_object_name = "mail_list"

# Просмотр всех пользователей (только для менеджера)
class UserListView(ManagerRequiredMixin, ListView):
    template_name = "services/user_list.html"
    model = User
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.all().order_by("-date_joined")


# Блокировка пользователя
class UserToggleActiveView(ManagerRequiredMixin, UpdateView):
    model = User
    fields = []

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            messages.error(request, "Вы не можете заблокировать себя!")
        else:
            user.is_active = not user.is_active
            user.save()
            status = "заблокирован" if not user.is_active else "разблокирован"
            messages.success(request, f"Пользователь {user.email} {status}")

        return redirect("services:user_list")


# Просмотр всех рассылок (для менеджера)
class AllMailingsListView(ManagerRequiredMixin, ListView):
    template_name = "services/all_mailings.html"
    model = Mailing
    context_object_name = "mailings"

    def get_queryset(self):
        return Mailing.objects.select_related("owner").all()


# Отключение рассылки (для менеджера)
class MailingToggleActiveView(ManagerRequiredMixin, UpdateView):
    model = Mailing
    fields = []

    def post(self, request, *args, **kwargs):
        mailing = self.get_object()
        mailing.status = "completed" if mailing.status == "started" else "started"
        mailing.save()

        status = "отключена" if mailing.status == "completed" else "включена"
        messages.success(request, f"Рассылка #{mailing.id} {status}")

        return redirect("services:all_mailings")
