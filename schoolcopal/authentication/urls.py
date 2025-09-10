from django.urls import path
from .views import (
    CustomLoginView, CustomLogoutView,
    CustomPasswordResetView, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView,
    admin_dashboard, enseignant_dashboard, parent_dashboard, directeur_dashboard
)

app_name = 'authentication'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('enseignant/dashboard/', enseignant_dashboard, name='enseignant_dashboard'),
    path('parent/dashboard/', parent_dashboard, name='parent_dashboard'),
    path('directeur/dashboard/', directeur_dashboard, name='directeur_dashboard'),
]