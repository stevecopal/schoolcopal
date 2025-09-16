from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import uuid


class BaseModel(models.Model):
    """
    Classe abstraite pour tous les modèles.
    Fournit ID auto-incrémenté, dates de création/modification, et soft delete.
    """
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date de création"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Date de modification"))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Date de suppression"))

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """Soft delete : définit deleted_at au lieu de supprimer."""
        self.deleted_at = timezone.now()
        self.save()

    def is_active(self):
        """True si non supprimé."""
        return self.deleted_at is None


class User(AbstractUser, BaseModel):
    """
    Modèle User pour authentification, étend AbstractUser et BaseModel.
    Attributs : username, email, role, telephone.
    """
    role = models.CharField(
        max_length=20,
        choices=[
            ('admin', _('Administrateur')),
            ('enseignant', _('Enseignant')),
            ('parent', _('Parent')),
            ('directeur', _('Directeur')),
        ],
        default='admin',
        verbose_name=_("Rôle")
    )
    telephone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(regex=r'^\6\d{8}$', message=_("Format téléphone camerounais : +237XXXXXXXX"))],
        verbose_name=_("Téléphone")
    )

    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def authenticate(self, password):
        """Vérification mot de passe."""
        return self.check_password(password)

    def get_permissions(self):
        """Permissions basées sur rôle."""
        permissions = {
            'admin': ['all'],
            'enseignant': ['saisir_notes', 'marquer_presence'],
            'parent': ['consulter_portail'],
            'directeur': ['voir_rapports']
        }
        return permissions.get(self.role, [])


class Ecole(BaseModel):
    nom = models.CharField(max_length=255, verbose_name=_("Nom de l'école"))
    adresse = models.TextField(verbose_name=_("Adresse"))
    type = models.CharField(
        max_length=20,
        choices=[('publique', _('Publique')), ('privee', _('Privée'))],
        default='privee',
        verbose_name=_("Type d'école")
    )
    nombre_classes = models.IntegerField(default=6, verbose_name=_("Nombre de classes"))

    class Meta:
        verbose_name = _("École")
        verbose_name_plural = _("Écoles")

    def __str__(self):
        return self.nom

    def generate_rapport(self):
        total_eleves = self.eleves.filter(deleted_at__isnull=True).count()
        return {"nom": self.nom, "total_eleves": total_eleves}
    
    @classmethod
    def get_default_ecole(cls):
        """Return the first active school or create a default one if none exists."""
        ecole = cls.objects.filter(deleted_at__isnull=True).first()
        if not ecole:
            ecole = cls.objects.create(
                nom="Default School",
                type="publique",
                adresse="Default Address",
            )
        return ecole


class ClasseScolaire(BaseModel):
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE, related_name='classes', verbose_name=_("École"))
    niveau = models.CharField(
        max_length=10,
        choices=[('SIL', 'SIL'), ('CP', 'CP'), ('CE1', 'CE1'), ('CE2', 'CE2'), ('CM1', 'CM1'), ('CM2', 'CM2')],
        verbose_name=_("Niveau")
    )
    section = models.CharField(max_length=5, blank=True, verbose_name=_("Section"))
    capacite = models.IntegerField(default=50, verbose_name=_("Capacité"))
    
    def get_eleves(self):
       
        return self.eleves.filter(deleted_at__isnull=True)
    
    def get_matieres(self):
        
        return self.matieres.filter(deleted_at__isnull=True)

    class Meta:
        verbose_name = _("Classe Scolaire")
        verbose_name_plural = _("Classes Scolaires")
        unique_together = ['ecole', 'niveau', 'section']

    def __str__(self):
        return f"{self.get_niveau_display()} {self.section or ''}"


class Matiere(BaseModel):
    classe = models.ForeignKey(
        ClasseScolaire,
        on_delete=models.CASCADE,
        related_name='matieres',
        verbose_name=_("Classe")
    )
    nom = models.CharField(max_length=100, verbose_name=_("Nom de la matière"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Matière")
        verbose_name_plural = _("Matières")
        unique_together = ['classe', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.classe})"


class Eleve(BaseModel):
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE, related_name='eleves', verbose_name=_("École"))
    classe = models.ForeignKey(
        ClasseScolaire,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eleves',
        verbose_name=_("Classe")
    )
    nom = models.CharField(max_length=100, verbose_name=_("Nom"))
    prenom = models.CharField(max_length=100, verbose_name=_("Prénom"))
    age = models.IntegerField(verbose_name=_("Âge"))
    date_naissance = models.DateField(blank=True, null=True, verbose_name=_("Date de naissance"))
    sexe = models.CharField(
        max_length=10,
        choices=[('garcon', _('Garçon')), ('fille', _('Fille'))],
        verbose_name=_("Sexe")
    )
    parent_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'parent'},
        related_name='enfants',
        verbose_name=_("Parent")
    )

    class Meta:
        verbose_name = _("Élève")
        verbose_name_plural = _("Élèves")

    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Enseignant(BaseModel):
    """Profil Enseignant lié à un User avec role='enseignant'."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="enseignant_profile")
    classe = models.OneToOneField(
        ClasseScolaire,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enseignant',
        verbose_name=_("Classe assignée")
    )
    salaire = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Salaire"))

    class Meta:
        verbose_name = _("Enseignant")
        verbose_name_plural = _("Enseignants")

    def __str__(self):
        return f"{self.user.username} - {self.classe or 'Sans classe'}"


class Frequence(BaseModel):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='frequents', verbose_name=_("Élève"))
    date = models.DateField(verbose_name=_("Date"))
    present = models.BooleanField(default=True, verbose_name=_("Présent"))
    raison_absence = models.TextField(blank=True, verbose_name=_("Raison absence"))

    class Meta:
        verbose_name = _("Fréquentation")
        verbose_name_plural = _("Fréquentations")
        unique_together = ['eleve', 'date']

    def __str__(self):
        return f"{self.eleve} - {self.date} ({'Présent' if self.present else 'Absent'})"


class Note(BaseModel):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='notes', verbose_name=_("Élève"))
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='notes', verbose_name=_("Matière"))
    valeur = models.DecimalField(max_digits=4, decimal_places=2, verbose_name=_("Note (0-20)"))
    trimestre = models.IntegerField(choices=[(1, '1er'), (2, '2e'), (3, '3e')], verbose_name=_("Trimestre"))
    sequence = models.IntegerField(choices=[(1, 'Séquence 1'), (2, 'Séquence 2'), (3, 'Séquence 3'),(4, 'Séquence 4'), (5, 'Séquence 5'), (6, 'Séquence 6')], null=True, blank=True)

    enseignant = models.ForeignKey(
        Enseignant,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notes_saisies',
        verbose_name=_("Enseignant")
    )

    class Meta:
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")
        unique_together = ['eleve', 'matiere', 'trimestre']

    def __str__(self):
        return f"{self.eleve} - {self.matiere}: {self.valeur}/20"


class Paiement(BaseModel):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='paiements', verbose_name=_("Élève"))
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Montant"))
    date_paiement = models.DateField(verbose_name=_("Date de paiement"))
    statut = models.CharField(
        max_length=20,
        choices=[('paye', _('Payé')), ('impaye', _('Impayé'))],
        default='impaye',
        verbose_name=_("Statut")
    )
    mode = models.CharField(
        max_length=20,
        choices=[('cash', _('Cash')), ('mobile_money', _('Mobile Money'))],
        verbose_name=_("Mode de paiement")
    )

    class Meta:
        verbose_name = _("Paiement")
        verbose_name_plural = _("Paiements")

    def __str__(self):
        return f"{self.eleve} - {self.montant} FCFA ({self.statut})"


class EmploiDuTemps(BaseModel):
    classe = models.ForeignKey(ClasseScolaire, on_delete=models.CASCADE, related_name='emplois', verbose_name=_("Classe"))
    jour = models.CharField(max_length=20, choices=[
        ('lundi', 'Lundi'), ('mardi', 'Mardi'), ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'), ('vendredi', 'Vendredi'), ('samedi', 'Samedi')
    ], verbose_name=_("Jour"))
    heure = models.TimeField(verbose_name=_("Heure"))
    salle = models.CharField(max_length=50, verbose_name=_("Salle"))

    class Meta:
        verbose_name = _("Emploi du Temps")
        verbose_name_plural = _("Emplois du Temps")
        ordering = ['jour', 'heure']

    def __str__(self):
        return f"{self.classe} - {self.jour} {self.heure}"


class Notification(BaseModel):
    destinataire = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_("Destinataire")
    )
    message = models.TextField(verbose_name=_("Message"))
    type = models.CharField(
        max_length=20,
        choices=[('sms', 'SMS'), ('email', 'Email')],
        verbose_name=_("Type")
    )
    envoye = models.BooleanField(default=False, verbose_name=_("Envoyé"))

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification pour {self.destinataire}: {self.message[:50]}..."
    
class PasswordResetCode(BaseModel):
    """Model to store password reset verification codes."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_codes', verbose_name=_("User"))
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_("Verification Code"))
    expires_at = models.DateTimeField(verbose_name=_("Expiration Date"))

    class Meta:
        verbose_name = _("Password Reset Code")
        verbose_name_plural = _("Password Reset Codes")

    def __str__(self):
        return f"Code for {self.user.username}: {self.code}"

    def is_valid(self):
        """Check if the code is still valid (not expired and not soft-deleted)."""
        return self.is_active() and self.expires_at > timezone.now()


# Signal : envoi d'email après création utilisateur
@receiver(post_save, sender=User)
def send_credentials(sender, instance, created, **kwargs):
    if created and instance.role != 'admin':
        raw_password = getattr(instance, "_raw_password", None)
        subject = _('Bienvenue sur CopalSchool - Vos identifiants')
        message = _(
            f'Bonjour {instance.username},\n\n'
            f'Votre compte a été créé par l’administration.\n'
            f'Nom d’utilisateur: {instance.username}\n\n'
            f"Mot de passe : {raw_password or '(non disponible)'}\n\n"

            f'Connectez-vous sur: http://yourdomain.com/auth/login/\n\n'
            f'-- L’équipe CopalSchool'
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email], fail_silently=True)
