from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from schoolcopal.models import User, Ecole, ClasseScolaire, Eleve, Enseignant, Paiement, Notification

@login_required
def directeur_dashboard(request):
    """
    Director dashboard: Global school stats, reports, users management.
    Only accessible if user.role == 'directeur'.
    """
    if request.user.role != 'directeur':
        return redirect('login')

    default_school = Ecole.get_default_ecole()  # Singleton school

    context = {
        'school': default_school,
        'total_students': default_school.eleves.filter(deleted_at__isnull=True).count(),
        'total_classes': default_school.classes.count(),
        'total_teachers': Enseignant.objects.filter(deleted_at__isnull=True).count(),
        'total_parents': User.objects.filter(role='parent', deleted_at__isnull=True).count(),
        'recent_report': default_school.generate_rapport(),  # From Ecole.generate_rapport()
        'title': _('Director Dashboard'),
    }
    return render(request, 'directeur/dashboard.html', context)