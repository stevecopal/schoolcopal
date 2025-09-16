from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from schoolcopal.models import PasswordResetCode, User
import uuid
from .models import User, Ecole, ClasseScolaire, Eleve, Enseignant, Matiere, Note

class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form with translated placeholders."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Username')}),
        label=_("Username")
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Password')}),
        label=_("Password")
    )

class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with email validation."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email address')}),
        label=_("Email")
    )

    def clean_email(self):
        """Verify if email exists in the database."""
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email, deleted_at__isnull=True).exists():
            raise ValidationError(_("No account is associated with this email address."))
        return email

class CustomSetPasswordForm(SetPasswordForm):
    """Custom form for setting new password."""
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('New password')}),
        label=_("New password")
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Confirm new password')}),
        label=_("Confirm new password")
    )

class VerificationCodeForm(forms.Form):
    """Form to verify the reset code."""
    verification_code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Verification Code')}),
        label=_("Verification Code")
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_verification_code(self):
        """Validate the verification code."""
        code = self.cleaned_data.get('verification_code')
        try:
            uuid_obj = uuid.UUID(code)
            reset_code = PasswordResetCode.objects.get(code=uuid_obj, user=self.user)
            if not reset_code.is_valid():
                raise ValidationError(_("The verification code is invalid or has expired."))
        except (ValueError, PasswordResetCode.DoesNotExist):
            raise ValidationError(_("Invalid verification code."))
        return code
    
from .models import Eleve, Enseignant, Matiere, ClasseScolaire, User

class EleveForm(forms.ModelForm):
    """Form for creating/updating Eleve."""
     # ➜ Champs supplémentaires pour le parent
    parent_name = forms.CharField(
        label=_("Parent Name"),
        max_length=150,
        required=True
    )
    parent_email = forms.EmailField(
        label=_("Parent Email"),
        required=True
    )
    parent_phone = forms.CharField(
        label=_("Parent Phone"),
        max_length=50,
        required=True
    )
    class Meta:
        model = Eleve
        fields = ['ecole', 'classe', 'nom', 'prenom', 'age', 'date_naissance', 'sexe',]
        labels = {
            'ecole': _('School'),
            'classe': _('Class'),
            'nom': _('Last Name'),
            'prenom': _('First Name'),
            'age': _('Age'),
            'date_naissance': _('Birth Date'),
            'sexe': _('Gender'),
            'parent_id': _('Parent'),
        }

class EnseignantForm(forms.ModelForm):
    """Form for creating/updating Enseignant and its related User."""

    # Champs User
    username = forms.CharField(label=_("Nom d’utilisateur"), required=True)
    email = forms.EmailField(label=_("Email"), required=True)
    telephone = forms.CharField(label=_("Téléphone"), required=False)
    first_name = forms.CharField(label=_("Prénom"), required=True)
    last_name = forms.CharField(label=_("Nom"), required=True)

    # Mot de passe → facultatif en mise à jour
    password1 = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput,
        required=False,
        help_text=_("Laisser vide pour conserver l’ancien mot de passe.")
    )
    password2 = forms.CharField(
        label=_("Confirmation mot de passe"),
        widget=forms.PasswordInput,
        required=False,
        help_text=_("Saisissez à nouveau le mot de passe.")
    )

    class Meta:
        model = Enseignant
        fields = ["classe", "salaire"]
        labels = {
            "classe": _("Classe assignée"),
            "salaire": _("Salaire"),
        }

    def clean(self):
        cleaned = super().clean()
        pwd1 = cleaned.get("password1")
        pwd2 = cleaned.get("password2")
        if pwd1 or pwd2:
            if pwd1 != pwd2:
                raise forms.ValidationError(_("Les mots de passe ne correspondent pas."))
        return cleaned

class MatiereForm(forms.ModelForm):
    """Form for creating/updating Matiere."""
    class Meta:
        model = Matiere
        fields = ['classe', 'nom', 'description']
        labels = {
            'classe': _('Class'),
            'nom': _('Subject Name'),
            'description': _('Description'),
        }

class ClasseScolaireForm(forms.ModelForm):
    """Form for creating/updating ClasseScolaire."""
    class Meta:
        model = ClasseScolaire
        fields = ['ecole', 'niveau', 'section', 'capacite']
        labels = {
            'ecole': _('School'),
            'niveau': _('Level'),
            'section': _('Section'),
            'capacite': _('Capacity'),
        }

class DirecteurForm(forms.ModelForm):
    """Form for creating/updating Directeur (User with role='directeur')."""
    password1 = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput,
        required=True
    )
    password2 = forms.CharField(
        label=_("Confirmation mot de passe"),
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'telephone']
        labels = {
            'username': _('Nom d’utilisateur'),
            'email': _('Email'),
            'telephone': _('Téléphone'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.role = 'directeur'  # Force role for Directeur

    def clean(self):
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get("password1")
        pwd2 = cleaned_data.get("password2")
        if pwd1 and pwd2 and pwd1 != pwd2:
            raise forms.ValidationError(_("Les mots de passe ne correspondent pas."))
        return cleaned_data
        
class NoteForm(forms.ModelForm):
    """Form for adding/updating Note with sequence."""
    sequence = forms.ChoiceField(
        choices=[(i, f"Séquence {i}") for i in range(1, 7)],
        label=_("Sequence"),
        required=True
    )

    class Meta:
        model = Note
        fields = ['eleve', 'matiere', 'valeur', 'trimestre', 'sequence']
        labels = {
            'eleve': _('Student'),
            'matiere': _('Subject'),
            'valeur': _('Value (0-20)'),
            'trimestre': _('Trimester'),
            'sequence': _('Sequence'),
        }
        widgets = {
            'valeur': forms.NumberInput(attrs={'step': '0.01', 'min': 0, 'max': 20}),
            'trimestre': forms.Select(choices=[('T1', 'Trimester 1'), ('T2', 'Trimester 2'), ('T3', 'Trimester 3')]),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher and teacher.classe:
            # Restrict students to those in the teacher's class
            self.fields['eleve'].queryset = Eleve.objects.filter(classe=teacher.classe, deleted_at__isnull=True)
            # Restrict subjects to those in the teacher's class
            self.fields['matiere'].queryset = Matiere.objects.filter(classe=teacher.classe, deleted_at__isnull=True)
            

class AdminForm(forms.ModelForm):
    """Form for creating/updating Admin users."""
    first_name = forms.CharField(label=_("First Name"), required=True)
    last_name = forms.CharField(label=_("Last Name"), required=True)
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label=_("Confirm Password"), widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'telephone', 'first_name', 'last_name']
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'telephone': _('Telephone'),
        }

    def clean(self):
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get("password1")
        pwd2 = cleaned_data.get("password2")
        if pwd1 or pwd2:
            if pwd1 != pwd2:
                raise forms.ValidationError(_("Passwords do not match."))
        return cleaned_data