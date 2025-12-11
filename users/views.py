from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View, TemplateView, UpdateView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    UserUpdateForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm
)
from .utils import (
    send_verification_email,
    send_password_reset_email,
    verify_email_token,
    verify_password_reset_token
)
from .models import User


class RegisterView(View):
    """Регистрация пользователя"""
    template_name = 'users/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('services:mailing_list')
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('services:mailing_list')

        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Деактивируем до подтверждения email
            user.save()

            # Отправляем email для подтверждения
            send_verification_email(user, request)

            messages.success(
                request,
                _('Регистрация успешна! Проверьте вашу почту для подтверждения email.')
            )
            return redirect('users:login')

        return render(request, self.template_name, {'form': form})


class LoginView(View):
    """Вход в систему"""
    template_name = 'users/login.html'
    success_url = reverse_lazy('services:mailing_list')

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('services:mailing_list')
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('services:mailing_list')

        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, _('Добро пожаловать!'))

                # Редирект на следующую страницу или домашнюю
                next_page = request.GET.get('next', 'services:mailing_list')
                return redirect(next_page)

        return render(request, self.template_name, {'form': form})


@login_required
def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, _('Вы успешно вышли из системы.'))
    return redirect('services:mailing_list')


class VerifyEmailView(View):
    """Подтверждение email"""
    template_name = 'users/verify_email.html'

    def get(self, request, token):
        user, success = verify_email_token(token)

        if success:
            messages.success(
                request,
                _('Email успешно подтвержден! Теперь вы можете войти в систему.')
            )
            return redirect('users:login')
        else:
            messages.error(
                request,
                _('Ссылка подтверждения недействительна или устарела.')
            )
            return render(request, self.template_name)


class ProfileView(LoginRequiredMixin, TemplateView):
    """Просмотр профиля"""
    template_name = 'users/profile.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""
    model = User
    form_class = UserUpdateForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _('Профиль успешно обновлен!'))
        return super().form_valid(form)


class PasswordResetView(View):
    """Запрос на сброс пароля"""
    template_name = 'users/password_reset.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = CustomPasswordResetForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('home')

        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = User.objects.get(email=email)
                # Отправляем email для сброса пароля
                send_password_reset_email(user, request)
            except User.DoesNotExist:
                pass  # Не показываем, что пользователь не существует

            messages.success(
                request,
                _('Инструкции по сбросу пароля отправлены на ваш email, если он зарегистрирован в системе.')
            )
            return redirect('users:login')

        return render(request, self.template_name, {'form': form})


class PasswordResetConfirmView(View):
    """Подтверждение сброса пароля"""
    template_name = 'users/password_reset_confirm.html'

    def get(self, request, token):
        user, valid = verify_password_reset_token(token)

        if not valid:
            messages.error(request, _('Ссылка сброса пароля недействительна или устарела.'))
            return redirect('users:password_reset')

        form = CustomSetPasswordForm(user)
        return render(request, self.template_name, {'form': form, 'token': token})

    def post(self, request, token):
        user, valid = verify_password_reset_token(token)

        if not valid:
            messages.error(request, _('Ссылка сброса пароля недействительна или устарела.'))
            return redirect('users:password_reset')

        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()

            # Помечаем токен как использованный
            from .models import PasswordResetToken
            PasswordResetToken.objects.filter(token=token).update(is_used=True)

            messages.success(request, _('Пароль успешно изменен! Теперь вы можете войти.'))
            return redirect('users:login')

        return render(request, self.template_name, {'form': form, 'token': token})