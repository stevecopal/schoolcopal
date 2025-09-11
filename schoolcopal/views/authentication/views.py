from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from schoolcopal.forms import CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm, VerificationCodeForm
from schoolcopal.models import PasswordResetCode, User
from django.utils import timezone
from datetime import timedelta

class CustomLoginView(LoginView):
    """Custom login view with role-based redirection."""
    form_class = CustomAuthenticationForm
    template_name = 'authentication/login.html'
    success_url = reverse_lazy('schoolcopal:admin_dashboard')

    def get_success_url(self):
        """Redirect to appropriate dashboard based on user role."""
        user = self.request.user
        if not user.is_active:
            return reverse_lazy('schoolcopal:login')
        role = user.role
        if role == 'admin':
            return reverse_lazy('schoolcopal:admin_dashboard')
        elif role == 'enseignant':
            return reverse_lazy('schoolcopal:enseignant_dashboard')
        elif role == 'parent':
            return reverse_lazy('schoolcopal:parent_dashboard')
        elif role == 'directeur':
            return reverse_lazy('schoolcopal:directeur_dashboard')
        return reverse_lazy('schoolcopal:admin_dashboard')

class CustomLogoutView(LogoutView):
    """Custom logout view redirecting to login page."""
    next_page = reverse_lazy('schoolcopal:login')

class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view with verification code generation."""
    form_class = CustomPasswordResetForm
    template_name = 'authentication/password_reset_form.html'
    email_template_name = 'authentication/password_reset_email.html'
    subject_template_name = 'authentication/password_reset_subject.txt'
    success_url = reverse_lazy('schoolcopal:password_reset_done')

    def form_valid(self, form):
        """Generate and save verification code before sending email."""
        email = form.cleaned_data['email']
        users = User.objects.filter(email=email, deleted_at__isnull=True)
        if users.exists():
            user = users.first()
            reset_code = PasswordResetCode.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=1)
            )
            self.extra_email_context = {'verification_code': reset_code.code}
            self.request.session['reset_email'] = email
            self.request.session['uidb64'] = self.get_uid(user)
            self.request.session['token'] = self.make_token(user)
        return super().form_valid(form)

    def get_uid(self, user):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        return urlsafe_base64_encode(force_bytes(user.pk))

    def make_token(self, user):
        from django.contrib.auth.tokens import default_token_generator
        return default_token_generator.make_token(user)

class CustomPasswordResetDoneView(View):
    """View to enter verification code."""
    template_name = 'authentication/password_reset_done.html'

    def get(self, request):
        form = VerificationCodeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = VerificationCodeForm(request.POST, user=None)
        if form.is_valid():
            email = request.session.get('reset_email')
            if not email or not User.objects.filter(email=email, deleted_at__isnull=True).exists():
                return render(request, self.template_name, {
                    'form': form,
                    'error': _("Invalid session. Please request a new password reset.")
                })
            user = User.objects.get(email=email, deleted_at__isnull=True)
            form = VerificationCodeForm(request.POST, user=user)
            if form.is_valid():
                return redirect('schoolcopal:password_reset_confirm', uidb64=request.session.get('uidb64'), token=request.session.get('token'))
        return render(request, self.template_name, {'form': form})

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """View for setting new password after code verification."""
    form_class = CustomSetPasswordForm
    template_name = 'authentication/password_reset_confirm.html'
    success_url = reverse_lazy('schoolcopal:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """View for password reset completion, redirects to login."""
    template_name = 'authentication/password_reset_complete.html'
    success_url = reverse_lazy('schoolcopal:login')