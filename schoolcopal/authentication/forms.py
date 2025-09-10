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