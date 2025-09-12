from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import models  # <-- pour pouvoir utiliser models.Avg
from ...models import Enseignant, Eleve, Matiere, Note  # nom sans accent
from ...forms import NoteForm

@login_required
def enseignant_dashboard(request):
    """
    Teacher dashboard: View class students with notes by subject, number of students, subject list, calculate average notes by trimester.
    Only accessible if user.role == 'enseignant'.
    """
    if request.user.role != 'enseignant':
        return redirect('schoolcopal:login')

    teacher = Enseignant.objects.get(user_id=request.user.id)
    assigned_class = teacher.classe

    if not assigned_class:
        messages.error(request, _('No class assigned. Contact admin.'))
        return render(request, 'enseignant/dashboard.html', {'title': _('Teacher Dashboard')})

    # List of students
    students = assigned_class.get_eleves()

    # Number of students
    total_students = students.count()

    # List of subjects for the class
    subjects = assigned_class.get_matieres()

    # Notes by student and subject
    notes_by_student = {student: Note.objects.filter(eleve=student, deleted_at__isnull=True).select_related('matiere') for student in students}

    # Average notes by trimester for each student
    averages_by_student = {}
    for student in students:
        averages = {}
        for trimestre in [1, 2, 3]:  # Assuming 3 trimesters
            avg = student.notes.filter(trimestre=trimestre, deleted_at__isnull=True).aggregate(avg=models.Avg('valeur'))['avg'] or 0
            averages[trimestre] = round(avg, 2)
        averages_by_student[student] = averages

    # # Recent attendance (optional addition for completeness)
    # recent_attendance = Fréquentation.objects.filter(
    #     eleve__classe=assigned_class, deleted_at__isnull=True
    # ).order_by('-date')[:10]

    context = {
        'assigned_class': assigned_class,
        'students': students,
        'total_students': total_students,
        'subjects': subjects,
        'notes_by_student': notes_by_student,
        'averages_by_student': averages_by_student,
        # 'recent_attendance': recent_attendance,
        'title': _('Teacher Dashboard'),
    }
    return render(request, 'enseignant/dashboard.html', context)

class NoteCreateView(CreateView):
    """View to add a note for a student."""
    model = Note
    form_class = NoteForm
    template_name = 'enseignant/note_form.html'
    success_url = reverse_lazy('schoolcopal:enseignant_dashboard')

    def form_valid(self, form):
        messages.success(self.request, _('Note added successfully.'))
        return super().form_valid(form)

class NoteUpdateView(UpdateView):
    """View to update a note for a student."""
    model = Note
    form_class = NoteForm
    template_name = 'enseignant/note_form.html'
    success_url = reverse_lazy('schoolcopal:enseignant_dashboard')

    def form_valid(self, form):
        messages.success(self.request, _('Note updated successfully.'))
        return super().form_valid(form)

class NoteDeleteView(DeleteView):
    """View to delete a note for a student."""
    model = Note
    success_url = reverse_lazy('schoolcopal:enseignant_dashboard')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, _('Note deleted successfully.'))
        return redirect(self.success_url)