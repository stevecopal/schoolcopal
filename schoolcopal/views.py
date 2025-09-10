
from django.shortcuts import render
from django.utils.translation import gettext as _

def home(request):
    """Vue de la page d'accueil"""
    return render(request, "home.html")