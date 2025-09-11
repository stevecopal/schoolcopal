from django.urls import path
from .views.home import views as home_views
from .views.authentication import views as auth_views
from .views.admin import views as admin_views
from .views.parent import views as parent_views
from .views.enseignant import views as enseignant_views
from .views.directeur import views as directeur_views

app_name = 'schoolcopal'

urlpatterns = [
    # Home URLs
    path('', home_views.home, name='home'),
    
    # Authentication URLs
    path('authentication/login/', auth_views.CustomLoginView.as_view(), name='login'),
    path('authentication/logout/', auth_views.CustomLogoutView.as_view(), name='logout'),
    path('authentication/password_reset/', auth_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('authentication/password_reset/done/', auth_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('authentication/reset/<uidb64>/<token>/', auth_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('authentication/reset/done/', auth_views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Admin URLs
    path('school-admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    
    # Parent URLs
    path('parent/dashboard/', parent_views.parent_dashboard, name='parent_dashboard'),
    
    # Enseignant URLs
    path('enseignant/dashboard/', enseignant_views.enseignant_dashboard, name='enseignant_dashboard'),
    
    # Directeur URLs
    path('directeur/dashboard/', directeur_views.directeur_dashboard, name='directeur_dashboard'),
]