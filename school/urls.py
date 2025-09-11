from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Pour changement de langue
    path('admin/', admin.site.urls),  # Django Admin
    path('', include('schoolcopal.urls')),  # URLs de l'app schoolcopal
]