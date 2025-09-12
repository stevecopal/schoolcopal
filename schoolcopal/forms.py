from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from schoolcopal.models import PasswordResetCode, User
import uuid

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
    class Meta:
        model = Eleve
        fields = ['ecole', 'classe', 'nom', 'prenom', 'age', 'date_naissance', 'sexe', 'parent_id']
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
    """Form for creating/updating Enseignant."""
    class Meta:
        model = Enseignant
        fields = ['classe', 'salaire']
        labels = {
            'classe': _('Assigned Class'),
            'salaire': _('Salary'),
        }

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
    class Meta:
        model = User
        fields = ['username', 'email', 'telephone']
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'telephone': _('Telephone'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.role = 'directeur'  # Force role for Directeur