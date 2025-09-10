from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from .forms import CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm, VerificationCodeForm
from schoolcopal.models import PasswordResetCode, User
from django.utils import timezone
from datetime import timedelta

class CustomLoginView(LoginView):
    """Custom login view with role-based redirection."""
    form_class = CustomAuthenticationForm
    template_name = 'authentication/login.html'
    success_url = reverse_lazy('dashboard')  # Fallback URL

    def get_success_url(self):
        """Redirect to appropriate dashboard based on user role."""
        user = self.request.user
        if not user.is_active:
            return reverse_lazy('authentication:login')  # Handle soft-deleted users
        role = user.role
        if role == 'admin':
            return reverse_lazy('authentication:admin_dashboard')
        elif role == 'enseignant':
            return reverse_lazy('authentication:enseignant_dashboard')
        elif role == 'parent':
            return reverse_lazy('authentication:parent_dashboard')
        elif role == 'directeur':
            return reverse_lazy('authentication:directeur_dashboard')
        return reverse_lazy('dashboard')  # Default fallback

class CustomLogoutView(LogoutView):
    """Custom logout view redirecting to login page."""
    next_page = reverse_lazy('authentication:login')

class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view with verification code generation."""
    form_class = CustomPasswordResetForm
    template_name = 'authentication/password_reset_form.html'
    email_template_name = 'authentication/password_reset_email.html'
    subject_template_name = 'authentication/password_reset_subject.txt'
    success_url = reverse_lazy('authentication:password_reset_done')

    def form_valid(self, form):
        """Generate and save verification code before sending email."""
        email = form.cleaned_data['email']
        users = User.objects.filter(email=email, deleted_at__isnull=True)
        if users.exists():
            user = users.first()
            # Create verification code
            reset_code = PasswordResetCode.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=1)  # Code expires in 1 hour
            )
            # Add code to email context
            self.extra_email_context = {'verification_code': reset_code.code}
        return super().form_valid(form)

class CustomPasswordResetDoneView(View):
    """View to enter verification code."""
    template_name = 'authentication/password_reset_done.html'

    def get(self, request):
        form = VerificationCodeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = VerificationCodeForm(request.POST, user=None)  # User will be set after email validation
        if form.is_valid():
            # Find user by email from session (stored in CustomPasswordResetView)
            email = request.session.get('reset_email')
            if not email or not User.objects.filter(email=email, deleted_at__isnull=True).exists():
                return render(request, self.template_name, {
                    'form': form,
                    'error': _("Invalid session. Please request a new password reset.")
                })
            user = User.objects.get(email=email, deleted_at__isnull=True)
            form = VerificationCodeForm(request.POST, user=user)
            if form.is_valid():
                return redirect('authentication:password_reset_confirm', uidb64=request.session.get('uidb64'), token=request.session.get('token'))
        return render(request, self.template_name, {'form': form})

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """View for setting new password after code verification."""
    form_class = CustomSetPasswordForm
    template_name = 'authentication/password_reset_confirm.html'
    success_url = reverse_lazy('authentication:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """View for password reset completion, redirects to login."""
    template_name = 'authentication/password_reset_complete.html'
    success_url = reverse_lazy('authentication:login')

def admin_dashboard(request):
    """Custom admin dashboard view, accessible only to admin users."""
    if not request.user.is_authenticated or request.user.role != 'admin' or not request.user.is_active:
        return redirect('authentication:login')
    return render(request, 'admin/admin_dashboard.html', {
        'title': _('Admin Dashboard'),
        'permissions': request.user.get_permissions(),
    })

def enseignant_dashboard(request):
    """Custom teacher dashboard view."""
    if not request.user.is_authenticated or request.user.role != 'enseignant' or not request.user.is_active():
        return redirect('authentication:login')
    return render(request, 'authentication/enseignant_dashboard.html', {
        'title': _('Teacher Dashboard'),
        'permissions': request.user.get_permissions(),
    })

def parent_dashboard(request):
    """Custom parent dashboard view."""
    if not request.user.is_authenticated or request.user.role != 'parent' or not request.user.is_active():
        return redirect('authentication:login')
    return render(request, 'authentication/parent_dashboard.html', {
        'title': _('Parent Dashboard'),
        'permissions': request.user.get_permissions(),
    })

def directeur_dashboard(request):
    """Custom director dashboard view."""
    if not request.user.is_authenticated or request.user.role != 'directeur' or not request.user.is_active():
        return redirect('authentication:login')
    return render(request, 'authentication/directeur_dashboard.html', {
        'title': _('Director Dashboard'),
        'permissions': request.user.get_permissions(),
    })