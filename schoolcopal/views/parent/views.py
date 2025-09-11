from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from schoolcopal.models import User, Ecole, ClasseScolaire, Eleve, Enseignant, Paiement, Notification,Note

@login_required
def parent_dashboard(request):
    """
    Parent dashboard: View children, recent notes, attendance, payments.
    Only accessible if user.role == 'parent'.
    """
    if request.user.role != 'parent':
        from django.shortcuts import redirect
        return redirect('login')  # Or raise 403

    # Get children (enfants)
    children = Eleve.objects.filter(parent_id=request.user, deleted_at__isnull=True).select_related('classe')

    context = {
        'children': children,
        'total_children': children.count(),
        'recent_notes': Note.objects.filter(
            eleve__parent_id=request.user,
            deleted_at__isnull=True
        ).select_related('eleve', 'matiere')[:5],  # Last 5 notes
    
        'pending_payments': Paiement.objects.filter(
            eleve__parent_id=request.user,
            statut='impaye',
            deleted_at__isnull=True
        ),
        'title': _('Parent Dashboard'),
    }
    return render(request, 'parent/dashboard.html', context)