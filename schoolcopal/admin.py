from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Ecole, ClasseScolaire, Eleve, Enseignant,
    Frequence, Note, Paiement, EmploiDuTemps, Notification, Matiere
)

# ============================
# ACTIONS COMMUNES
# ============================

@admin.action(description=_("Marquer comme supprimé (soft delete)"))
def mark_as_deleted(modeladmin, request, queryset):
    """Action admin pour soft delete en masse."""
    queryset.update(deleted_at=timezone.now())


# ============================
# USER
# ============================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin pour User (tous rôles : admin, enseignant, parent, directeur)."""

    fieldsets = BaseUserAdmin.fieldsets + (
        (_("Champs personnalisés"), {'fields': ('role', 'telephone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'classes': ('wide',),
                'fields': ('email', 'role', 'telephone')}),
    )

    list_display = ['username', 'role', 'email', 'telephone', 'created_at', 'is_active']
    list_filter = ['role', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'telephone']
    actions = [mark_as_deleted]
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


# ============================
# ECOLE
# ============================

@admin.register(Ecole)
class EcoleAdmin(admin.ModelAdmin):
    """Admin pour Ecole."""
    list_display = ['nom', 'type', 'adresse', 'nombre_classes', 'created_at', 'is_active']
    list_filter = ['type']
    search_fields = ['nom', 'adresse']
    actions = [mark_as_deleted]
    list_per_page = 10

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


# ============================
# MATIERE
# ============================

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    """Admin pour Matiere."""
    list_display = ['nom', 'classe', 'created_at', 'is_active']
    list_filter = ['classe__niveau', 'classe__ecole__nom']
    search_fields = ['nom', 'classe__niveau']
    actions = [mark_as_deleted]
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True).select_related('classe__ecole')


# ============================
# CLASSE
# ============================

@admin.register(ClasseScolaire)
class ClasseScolaireAdmin(admin.ModelAdmin):
    """Admin pour ClasseScolaire."""
    list_display = ['niveau', 'section', 'capacite', 'enseignant', 'ecole', 'created_at', 'is_active']
    list_filter = ['niveau', 'ecole__nom']
    search_fields = ['niveau', 'section', 'enseignant__user__username']
    actions = [mark_as_deleted]
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True).select_related('ecole', 'enseignant')


# ============================
# ELEVE
# ============================

@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    """Admin pour Eleve."""
    list_display = ['prenom', 'nom', 'age', 'sexe', 'classe', 'parent_id', 'get_ecole', 'created_at', 'is_active']
    list_filter = ['sexe', 'classe__niveau', 'classe__ecole__nom', 'parent_id__username']
    search_fields = ['nom', 'prenom', 'parent_id__username']
    actions = [mark_as_deleted]
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)\
            .select_related('classe', 'parent_id')\
            .prefetch_related('classe__ecole')

    def get_ecole(self, obj):
        return obj.classe.ecole.nom if obj.classe and obj.classe.ecole else _("Non assigné")
    get_ecole.short_description = _("École")
    get_ecole.admin_order_field = 'classe__ecole__nom'


# ============================
# ENSEIGNANT
# ============================

@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    """Admin pour Enseignant."""
    list_display = ['user', 'classe', 'salaire', 'created_at', 'is_active']
    list_filter = ['classe__niveau', 'classe__ecole__nom']
    search_fields = ['user__username', 'user__telephone', 'classe__niveau']
    actions = [mark_as_deleted]
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True).select_related('classe', 'user')


# ============================
# FREQUENCE
# ============================

@admin.register(Frequence)
class FrequenceAdmin(admin.ModelAdmin):
    """Admin pour Fréquence (présences)."""
    list_display = ['eleve', 'date', 'present', 'raison_absence', 'created_at', 'is_active']
    list_filter = ['present', 'date', 'eleve__classe__niveau']
    search_fields = ['eleve__nom', 'eleve__prenom', 'raison_absence']
    actions = [mark_as_deleted]
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True).select_related('eleve__classe')


# ============================
# NOTE
# ============================

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Admin pour Note."""
    list_display = ['eleve', 'get_matiere_nom', 'valeur', 'trimestre', 'enseignant', 'created_at', 'is_active']
    list_filter = ['trimestre', 'matiere__nom', 'eleve__classe__niveau']
    search_fields = ['eleve__nom', 'eleve__prenom', 'matiere__nom']
    actions = [mark_as_deleted]
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)\
            .select_related('eleve', 'matiere', 'enseignant')

    def get_matiere_nom(self, obj):
        return obj.matiere.nom
    get_matiere_nom.short_description = _("Matière")
    get_matiere_nom.admin_order_field = 'matiere__nom'


# ============================
# PAIEMENT
# ============================

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    """Admin pour Paiement."""
    list_display = ['eleve', 'montant', 'date_paiement', 'statut', 'mode', 'created_at', 'is_active']
    list_filter = ['statut', 'mode', 'date_paiement']
    search_fields = ['eleve__nom', 'eleve__prenom']
    actions = [mark_as_deleted]
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True).select_related('eleve')


# ============================
# EMPLOI DU TEMPS
# ============================

@admin.register(EmploiDuTemps)
class EmploiDuTempsAdmin(admin.ModelAdmin):
    """Admin pour EmploiDuTemps."""
    list_display = ['classe', 'jour', 'heure', 'salle', 'created_at', 'is_active']
    list_filter = ['jour', 'classe__niveau']
    search_fields = ['classe__niveau', 'salle']
    actions = [mark_as_deleted]
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True).select_related('classe')


# ============================
# NOTIFICATION
# ============================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin pour Notification."""
    list_display = ['destinataire', 'type', 'message', 'envoye', 'created_at', 'is_active']
    list_filter = ['type', 'envoye', 'created_at']
    search_fields = ['destinataire__username', 'message']
    actions = [mark_as_deleted]
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True).select_related('destinataire')
