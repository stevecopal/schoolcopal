from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from ...models import User, Ecole, ClasseScolaire, Eleve, Enseignant, Matiere, Paiement, Notification
from ...forms import EleveForm, EnseignantForm, MatiereForm, ClasseScolaireForm, DirecteurForm,AdminForm
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

@login_required
def admin_dashboard(request):
    """
    Admin dashboard: Overview of school stats, users, classes, payments, notifications.
    Only accessible if user.role == 'admin'.
    """
    if request.user.role != 'admin':
        return redirect('schoolcopal:login')

    default_school = Ecole.get_default_ecole()

    # Liste des élèves classés par classe (salle)
    classes = ClasseScolaire.objects.filter(ecole=default_school, deleted_at__isnull=True)
    eleves_by_class = {classe: Eleve.objects.filter(classe=classe, deleted_at__isnull=True) for classe in classes}
    eleves_count_by_class = {classe: eleves_by_class[classe].count() for classe in classes}

    # Liste des enseignants avec classe et salaire
    enseignants = Enseignant.objects.filter(deleted_at__isnull=True).select_related('classe', 'user')

    # Liste des matières par classe
    matieres_by_class = {classe: classe.get_matieres() for classe in classes}

    # Liste des directeurs
    directeurs = User.objects.filter(role='directeur', deleted_at__isnull=True)

    # Liste des admins
    admins = User.objects.filter(role='admin', deleted_at__isnull=True)

    context = {
        'school': default_school,
        'eleves_by_class': eleves_by_class,
        'eleves_count_by_class': eleves_count_by_class,
        'enseignants': enseignants,
        'matieres_by_class': matieres_by_class,
        'directeurs': directeurs,
        'admins': admins,  # Ajouté pour afficher dans le tableau
        'total_admins': admins.count(),  # Pour les statistiques
        'total_students': default_school.eleves.filter(deleted_at__isnull=True).count(),
        'total_classes': classes.count(),
        'total_teachers': enseignants.count(),
        'total_users': User.objects.filter(deleted_at__isnull=True).count(),
        'classes': classes,  # Ajouté pour la liste des classes
        'pending_payments': Paiement.objects.filter(statut='impaye', deleted_at__isnull=True).count(),
        'recent_notifications': Notification.objects.filter(deleted_at__isnull=True).order_by('-created_at')[:5],
        'title': _('Admin Dashboard'),
    }
    return render(request, 'admin/dashboard.html', context)

# CRUD for Eleve
class EleveListView(ListView):
    model = Eleve
    template_name = 'admin/eleve_list.html'
    context_object_name = 'eleves'
    paginate_by = 20

    def get_queryset(self):
        return Eleve.objects.filter(deleted_at__isnull=True)

class EleveCreateView(CreateView):
    model = Eleve
    form_class = EleveForm
    template_name = 'admin/eleve_form.html'
    success_url = reverse_lazy('schoolcopal:eleve_list')

    def form_valid(self, form):
        messages.success(self.request, _('Student created successfully.'))
        return super().form_valid(form)

class EleveUpdateView(UpdateView):
    model = Eleve
    form_class = EleveForm
    template_name = 'admin/eleve_form.html'
    success_url = reverse_lazy('schoolcopal:eleve_list')

    def form_valid(self, form):
        messages.success(self.request, _('Student updated successfully.'))
        return super().form_valid(form)

class EleveDeleteView(DeleteView):
    model = Eleve
    template_name = "admin/eleve_confirm_delete.html"
    success_url = reverse_lazy('schoolcopal:eleve_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, _('Student deleted successfully.'))
        return redirect(self.success_url)

# CRUD for Enseignant
class EnseignantListView(ListView):
    model = Enseignant
    template_name = 'admin/enseignant_list.html'
    context_object_name = 'enseignants'
    paginate_by = 20

    def get_queryset(self):
        return Enseignant.objects.filter(deleted_at__isnull=True)

class EnseignantCreateView(CreateView):
    model = Enseignant
    form_class = EnseignantForm
    template_name = 'admin/enseignant_form.html'
    success_url = reverse_lazy('schoolcopal:enseignant_list')

    def form_valid(self, form):
        # 1️⃣ Créer le User lié
        user = User(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            telephone=form.cleaned_data["telephone"],
            role="enseignant"
        )
        raw_password = form.cleaned_data["password1"]
        user.set_password(raw_password)
        user._raw_password = raw_password  # pour le signal
        user.save()

        # 2️⃣ Créer l'enseignant et lui assigner le user
        instance = form.save(commit=False)
        instance.user = user
        instance.save()

        messages.success(self.request, _("Enseignant créé avec succès."))
        return redirect(self.success_url)

class EnseignantUpdateView(UpdateView):
    model = Enseignant
    form_class = EnseignantForm
    template_name = 'admin/enseignant_form.html'
    success_url = reverse_lazy('schoolcopal:enseignant_list')

    def form_valid(self, form):
        messages.success(self.request, _('Teacher updated successfully.'))
        return super().form_valid(form)

class EnseignantDeleteView(DeleteView):
    model = Enseignant
    template_name = "admin/enseignant_confirm_delete.html"
    success_url = reverse_lazy('schoolcopal:enseignant_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, _('Teacher deleted successfully.'))
        return redirect(self.success_url)

# CRUD for Matiere
class MatiereListView(ListView):
    model = Matiere
    template_name = 'admin/matiere_list.html'
    context_object_name = 'matieres'
    paginate_by = 20

    def get_queryset(self):
        return Matiere.objects.filter(deleted_at__isnull=True)

class MatiereCreateView(CreateView):
    model = Matiere
    form_class = MatiereForm
    template_name = 'admin/matiere_form.html'
    success_url = reverse_lazy('schoolcopal:matiere_list')

    def form_valid(self, form):
        messages.success(self.request, _('Subject created successfully.'))
        return super().form_valid(form)

class MatiereUpdateView(UpdateView):
    model = Matiere
    form_class = MatiereForm
    template_name = 'admin/matiere_form.html'
    success_url = reverse_lazy('schoolcopal:matiere_list')

    def form_valid(self, form):
        messages.success(self.request, _('Subject updated successfully.'))
        return super().form_valid(form)

class MatiereDeleteView(DeleteView):
    model = Matiere
    template_name = "admin/matiere_confirm_delete.html"
    success_url = reverse_lazy('schoolcopal:matiere_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, _('Subject deleted successfully.'))
        return redirect(self.success_url)

# CRUD for ClasseScolaire
class ClasseScolaireListView(ListView):
    model = ClasseScolaire
    template_name = 'admin/classescolaire_list.html'
    context_object_name = 'classes'
    paginate_by = 20

    def get_queryset(self):
        return ClasseScolaire.objects.filter(deleted_at__isnull=True)

class ClasseScolaireCreateView(CreateView):
    model = ClasseScolaire
    form_class = ClasseScolaireForm
    template_name = 'admin/classescolaire_form.html'
    success_url = reverse_lazy('schoolcopal:classescolaire_list')

    def form_valid(self, form):
        messages.success(self.request, _('Class created successfully.'))
        return super().form_valid(form)

class ClasseScolaireUpdateView(UpdateView):
    model = ClasseScolaire
    form_class = ClasseScolaireForm
    template_name = 'admin/classescolaire_form.html'
    success_url = reverse_lazy('schoolcopal:classescolaire_list')

    def form_valid(self, form):
        messages.success(self.request, _('Class updated successfully.'))
        return super().form_valid(form)

class ClasseScolaireDeleteView(DeleteView):
    model = ClasseScolaire
    template_name = "admin/classescolaire_confirm_delete.html"
    success_url = reverse_lazy('schoolcopal:classescolaire_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, _('Class deleted successfully.'))
        return redirect(self.success_url)

# CRUD for Directeur (User with role='directeur')
class DirecteurListView(ListView):
    model = User
    template_name = 'admin/directeur_list.html'
    context_object_name = 'directeurs'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.filter(role='directeur', deleted_at__isnull=True)

class DirecteurCreateView(CreateView):
    model = User
    form_class = DirecteurForm
    template_name = 'admin/directeur_form.html'
    success_url = reverse_lazy('schoolcopal:directeur_list')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.role = 'directeur'

        raw_password = form.cleaned_data.get("password")
        if raw_password:
            instance.set_password(raw_password)
            instance._raw_password = raw_password

        instance.save()
        messages.success(self.request, _('Director created successfully.'))
        return redirect(self.success_url)

class DirecteurUpdateView(UpdateView):
    model = User
    form_class = DirecteurForm
    template_name = 'admin/directeur_form.html'
    success_url = reverse_lazy('schoolcopal:directeur_list')

    def form_valid(self, form):
        messages.success(self.request, _('Director updated successfully.'))
        return super().form_valid(form)

class DirecteurDeleteView(DeleteView):
    model = User
    template_name = "admin/directeur_confirm_delete.html"
    success_url = reverse_lazy('schoolcopal:directeur_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, _('Director deleted successfully.'))
        return redirect(self.success_url)
    
    
# class ParentCreateView(CreateView):
#     model = User
#     form_class = ParentForm  # supposons que tu as ce formulaire
#     template_name = 'admin/parent_form.html'
#     success_url = reverse_lazy('schoolcopal:parent_list')

#     def form_valid(self, form):
#         instance = form.save(commit=False)
#         instance.role = 'parent'

#         raw_password = form.cleaned_data.get("password")
#         if raw_password:
#             instance.set_password(raw_password)
#             instance._raw_password = raw_password

#         instance.save()
#         messages.success(self.request, _('Parent created successfully.'))
#         return redirect(self.success_url)

User = get_user_model()

# Mixin pour restreindre l'accès aux admins
class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'


# Liste des admins
class AdminListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'admin/admin_list.html'
    context_object_name = 'admins'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.filter(role='admin', deleted_at__isnull=True)


# Créer un admin
class AdminCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = AdminForm
    template_name = 'admin/admin_form.html'
    success_url = reverse_lazy('schoolcopal:admin_list')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.role = 'admin'
        raw_password = form.cleaned_data["password1"]
        instance.set_password(raw_password)
        instance._raw_password = raw_password
        instance.save()

        # Send email with credentials
        subject = _('Welcome to CopalSchool - Your Admin Credentials')
        message = _(
            f'Hello {instance.username},\n\n'
            f'Your admin account has been created.\n'
            f'Username: {instance.username}\n'
            f'Password: {raw_password}\n\n'
            f'Login here: http://yourdomain.com/auth/login/\n\n'
            f'-- CopalSchool Team'
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email], fail_silently=True)

        messages.success(self.request, _("Admin created successfully and credentials sent by email."))
        return super().form_valid(form)


# Modifier un admin
class AdminUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = AdminForm
    template_name = 'admin/admin_form.html'
    success_url = reverse_lazy('schoolcopal:admin_list')

    def get_queryset(self):
        return User.objects.filter(role='admin', deleted_at__isnull=True)

    def form_valid(self, form):
        instance = form.save(commit=False)
        pwd = form.cleaned_data.get("password1")
        if pwd:
            instance.set_password(pwd)
            instance._raw_password = pwd

            # Send email with new credentials if password changed
            subject = _('Your Admin Password has been Updated')
            message = _(
                f'Hello {instance.username},\n\n'
                f'Your admin account password has been updated.\n'
                f'Username: {instance.username}\n'
                f'New Password: {pwd}\n\n'
                f'Login here: http://yourdomain.com/auth/login/\n\n'
                f'-- CopalSchool Team'
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email], fail_silently=True)

        instance.save()
        messages.success(self.request, _("Admin updated successfully."))
        return super().form_valid(form)


# Supprimer un admin (soft delete)
class AdminDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'admin/admin_confirm_delete.html'
    success_url = reverse_lazy('schoolcopal:admin_list')

    def get_queryset(self):
        return User.objects.filter(role='admin', deleted_at__isnull=True)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.deleted_at = timezone.now()
        self.object.save()
        messages.success(self.request, _("Admin deleted successfully."))
        return super().delete(request, *args, **kwargs)