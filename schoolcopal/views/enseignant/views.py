from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from schoolcopal.models import User, Ecole, ClasseScolaire, Eleve, Enseignant, Paiement, Notification, Note

@login_required
def enseignant_dashboard(request):
    """
    Teacher dashboard: Assigned class, students, subjects, notes to enter, attendance.
    Only accessible if user.role == 'enseignant'.
    """
    if request.user.role != 'enseignant':
        return redirect('login')

    teacher = Enseignant.objects.get(id=request.user.id)  # Get teacher instance
    assigned_class = teacher.classe  # From Enseignant.classe OneToOneField

    if not assigned_class:
        context = {
            'message': _('No class assigned. Contact admin.'),
            'title': _('Teacher Dashboard'),
        }
        return render(request, 'enseignant/dashboard.html', context)

    # Get students in class
    students = assigned_class.get_eleves()  # From ClasseScolaire.get_eleves()

    context = {
        'assigned_class': assigned_class,
        'students': students,
        'total_students': students.count(),
        'subjects': assigned_class.get_matieres(),  # Matières de la classe
        'notes_to_enter': Note.objects.filter(
            enseignant=teacher,
            trimestre=1,  # Current trimester example
            deleted_at__isnull=True
        ).count(),  # Count notes for current trimester
        
        'title': _('Teacher Dashboard'),
    }
    return render(request, 'enseignant/dashboard.html', context)