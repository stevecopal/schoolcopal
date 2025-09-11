from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from schoolcopal.models import User, Ecole, ClasseScolaire, Eleve, Enseignant, Paiement, Notification

@login_required
def admin_dashboard(request):
    """
    Admin dashboard: Overview of school stats, users, classes, payments, notifications.
    Only accessible if user.role == 'admin'.
    """
    if request.user.role != 'admin':
        return redirect('authentication:login')

    # default_school = Ecole.get_default_ecole()

    # context = {
    #     'school': default_school,
    #     'total_users': User.objects.filter(deleted_at__isnull=True).count(),
    #     'total_students': default_school.eleves.filter(deleted_at__isnull=True).count(),
    #     'total_teachers': Enseignant.objects.filter(deleted_at__isnull=True).count(),
    #     'total_parents': User.objects.filter(role='parent', deleted_at__isnull=True).count(),
    #     'total_classes': default_school.classes.filter(deleted_at__isnull=True).count(),
    #     'pending_payments': Paiement.objects.filter(
    #         statut='impaye',
    #         deleted_at__isnull=True
    #     ).count(),
    #     'recent_notifications': Notification.objects.filter(
    #         deleted_at__isnull=True
    #     ).order_by('-created_at')[:5],
    #     'title': _('Admin Dashboard'),
    # }
    return render(request, 'admin/dashboard.html', )