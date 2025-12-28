from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # Регистрация и активация
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "verify-email/<str:token>/",
        views.VerifyEmailView.as_view(),
        name="verify_email",
    ),
    # Авторизация
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Профиль
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="profile_edit"),
    # Сброс пароля
    path("password-reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/<str:token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
