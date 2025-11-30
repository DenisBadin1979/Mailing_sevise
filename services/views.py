from django.shortcuts import render
from django.views.generic import TemplateView



class BaseView(TemplateView):
    template_name = "services/base.html"