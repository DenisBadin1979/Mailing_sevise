from django.shortcuts import render


def base_1(request):
    return render(request, "services/base.html")
