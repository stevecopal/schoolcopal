from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _

@shared_task
def send_credentials_email(email, username, password):
    """
    Async task to send credentials after user creation.
    """
    subject = _('Welcome to CopalSchool - Your Login Credentials')
    message = _(
        f'Dear User,\n\n'
        f'Your account has been created.\n'
        f'Username: {username}\n'
        f'Password: {password}\n\n'
        f'Login at: http://yourdomain.com/auth/login/\n\n'
        f'Best regards,\nCopalSchool Team'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

@shared_task
def send_reset_code_email(email, code):
    """
    Async task to send reset code.
    """
    subject = _('Password Reset Code - CopalSchool')
    message = _(
        f'Your reset code is: {code}\n'
        f'It expires in 10 minutes.\n\n'
        f'Best regards,\nCopalSchool Team'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])