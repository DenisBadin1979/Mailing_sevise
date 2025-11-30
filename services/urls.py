from services.apps import ServicesConfig
from django.urls import path
from services.views import BaseView

app_name = ServicesConfig.name


urlpatterns = [

    path("", BaseView.as_view(), name="index"),
]
