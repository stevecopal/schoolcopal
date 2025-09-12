from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from ...models import Eleve, Note
from django.db.models import Avg

@login_required
def parent_dashboard(request):
    """
    Parent dashboard: View all information about their children, notes by subject, and averages by trimester.
    Only accessible if user.role == 'parent'.
    """
    if request.user.role != 'parent':
        return redirect('schoolcopal:login')

    # Get the children of the parent
    children = Eleve.objects.filter(parent_id=request.user, deleted_at__isnull=True).select_related('classe')

    children_data = []
    for child in children:
        # Notes by subject
        notes_by_subject = {}
        subjects = child.classe.matieres.all() if child.classe else []
        for subject in subjects:
            notes = Note.objects.filter(eleve=child, matiere=subject, deleted_at__isnull=True).order_by('trimestre')
            notes_by_subject[subject] = notes

        # Averages by trimester (using integers 1,2,3)
        averages = {}
        for trimestre in [1, 2, 3]:
            avg = child.notes.filter(trimestre=trimestre, deleted_at__isnull=True).aggregate(avg=Avg('valeur'))['avg'] or 0
            averages[trimestre] = round(avg, 2)

        children_data.append({
            'child': child,
            'notes_by_subject': notes_by_subject,
            'averages': averages,
        })

    context = {
        'children_data': children_data,
        'title': _('Parent Dashboard'),
    }
    return render(request, 'parent/dashboard.html', context)
