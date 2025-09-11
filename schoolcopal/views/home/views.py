from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

def home(request):
    """Home page view."""
    context = {
        'title': _('Welcome to CopalSchool'),
    }
    return render(request, 'home.html', context)