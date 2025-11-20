from services.apps import ServicesConfig
from django.urls import path
from services.views import base_1


app_name = ServicesConfig.name


urlpatterns = [

    path("", base_1, name="index"),
]
