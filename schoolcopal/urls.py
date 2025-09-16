from django.urls import path

# Home
from schoolcopal.views.home import views as home_views

# Authentication
from schoolcopal.views.authentication import views as auth_views

# Admin (dashboard + CRUD)
from schoolcopal.views.admin import views as admin_views

# Parent / Enseignant / Directeur dashboards
from schoolcopal.views.parent import views as parent_views
from schoolcopal.views.enseignant import views as enseignant_views
from schoolcopal.views.directeur import views as directeur_views
from .views.enseignant.views import enseignant_dashboard, NoteCreateView, NoteUpdateView, NoteDeleteView

app_name = "schoolcopal"

urlpatterns = [
    # ---------------------- Home ----------------------
    path("", home_views.home, name="home"),

    # ---------------- Authentication -----------------
    path("authentication/login/", auth_views.CustomLoginView.as_view(), name="login"),
    path("authentication/logout/", auth_views.CustomLogoutView.as_view(), name="logout"),
    path("authentication/password_reset/", auth_views.CustomPasswordResetView.as_view(), name="password_reset"),
    path("authentication/password_reset/done/", auth_views.CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("authentication/reset/<uidb64>/<token>/", auth_views.CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("authentication/reset/done/", auth_views.CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # ---------------------- Admin ---------------------
    path("school-admin/dashboard/", admin_views.admin_dashboard, name="admin_dashboard"),

    # Élèves
    path("school-admin/eleves/", admin_views.EleveListView.as_view(), name="eleve_list"),
    path("school-admin/eleves/create/", admin_views.EleveCreateView.as_view(), name="eleve_create"),
    path("school-admin/eleves/update/<pk>/", admin_views.EleveUpdateView.as_view(), name="eleve_update"),
    path("school-admin/eleves/delete/<pk>/", admin_views.EleveDeleteView.as_view(), name="eleve_delete"),

    # Enseignants
    path("school-admin/enseignants/", admin_views.EnseignantListView.as_view(), name="enseignant_list"),
    path("school-admin/enseignants/create/", admin_views.EnseignantCreateView.as_view(), name="enseignant_create"),
    path("school-admin/enseignants/update/<pk>/", admin_views.EnseignantUpdateView.as_view(), name="enseignant_update"),
    path("school-admin/enseignants/delete/<pk>/", admin_views.EnseignantDeleteView.as_view(), name="enseignant_delete"),

    # Matières
    path("school-admin/matieres/", admin_views.MatiereListView.as_view(), name="matiere_list"),
    path("school-admin/matieres/create/", admin_views.MatiereCreateView.as_view(), name="matiere_create"),
    path("school-admin/matieres/update/<pk>/", admin_views.MatiereUpdateView.as_view(), name="matiere_update"),
    path("school-admin/matieres/delete/<pk>/", admin_views.MatiereDeleteView.as_view(), name="matiere_delete"),

    # Classes
    path("school-admin/classes/", admin_views.ClasseScolaireListView.as_view(), name="classescolaire_list"),
    path("school-admin/classes/create/", admin_views.ClasseScolaireCreateView.as_view(), name="classescolaire_create"),
    path("school-admin/classes/update/<pk>/", admin_views.ClasseScolaireUpdateView.as_view(), name="classescolaire_update"),
    path("school-admin/classes/delete/<pk>/", admin_views.ClasseScolaireDeleteView.as_view(), name="classescolaire_delete"),

    # Directeurs
    path("school-admin/directeurs/", admin_views.DirecteurListView.as_view(), name="directeur_list"),
    path("school-admin/directeurs/create/", admin_views.DirecteurCreateView.as_view(), name="directeur_create"),
    path("school-admin/directeurs/update/<pk>/", admin_views.DirecteurUpdateView.as_view(), name="directeur_update"),
    path("school-admin/directeurs/delete/<pk>/", admin_views.DirecteurDeleteView.as_view(), name="directeur_delete"),
    
    #admin
    path('admins/', admin_views.AdminListView.as_view(), name='admin_list'),
    path('admins/create/', admin_views.AdminCreateView.as_view(), name='admin_create'),
    path('admins/<int:pk>/update/', admin_views.AdminUpdateView.as_view(), name='admin_update'),
    path('admins/<int:pk>/delete/', admin_views.AdminDeleteView.as_view(), name='admin_delete'),

    # ---------------------- Parent --------------------
    path("parent/dashboard/", parent_views.parent_dashboard, name="parent_dashboard"),

    # ------------------- Enseignant -------------------
    path('enseignant/dashboard/', enseignant_dashboard, name='enseignant_dashboard'),
    # URLs pour les notes des enseignants
    path('enseignant/notes/create/<int:eleve_id>/', NoteCreateView.as_view(), name='note_create'),
    path('enseignant/notes/update/<int:pk>/', NoteUpdateView.as_view(), name='note_update'),
    path('enseignant/notes/delete/<int:pk>/', NoteDeleteView.as_view(), name='note_delete'),

    # ------------------- Directeur --------------------
    path("directeur/dashboard/", directeur_views.directeur_dashboard, name="directeur_dashboard"),
]
