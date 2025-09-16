from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import models
from ...models import Enseignant, Eleve, Matiere, Note
from ...forms import NoteForm

@login_required
def enseignant_dashboard(request):
    """
    Teacher dashboard: View all student info, subjects, notes by subject/trimestre/sequence, and averages by sequence/trimestre.
    Only accessible if user.role == 'enseignant'.
    """
    if request.user.role != 'enseignant':
        return redirect('schoolcopal:login')

    teacher = Enseignant.objects.get(user_id=request.user.id)
    assigned_class = teacher.classe

    if not assigned_class:
        messages.error(request, _('No class assigned. Contact admin.'))
        return render(request, 'enseignant/dashboard.html', {'title': _('Teacher Dashboard')})

    # List of students with all info
    students = assigned_class.get_eleves().select_related('classe')

    # Number of students
    total_students = students.count()

    # List of subjects for the class
    subjects = assigned_class.get_matieres()

    # Notes by student, subject, trimestre, and sequence
    notes_by_student = {}
    for student in students:
        notes_by_subject = {}
        for subject in subjects:
            notes_by_trimester = {}
            for trimestre in [1,2,3]:
                notes = Note.objects.filter(
                    eleve=student, matiere=subject, trimestre=trimestre, deleted_at__isnull=True
                ).order_by('sequence')
                notes_by_trimester[trimestre] = notes
            notes_by_subject[subject] = notes_by_trimester
        notes_by_student[student] = notes_by_subject

    # Averages by sequence and trimester for each student
    averages_by_student = {}
    for student in students:
        averages = {'by_sequence': {}, 'by_trimester': {}}
        for trimestre in [1,2,3]:
            # Average by trimester
            avg_trimester = student.notes.filter(
                trimestre=trimestre, deleted_at__isnull=True
            ).aggregate(avg=models.Avg('valeur'))['avg'] or 0
            averages['by_trimester'][trimestre] = round(avg_trimester, 2)
            # Average by sequence
            for sequence in range(1, 7):
                avg_sequence = student.notes.filter(
                    trimestre=trimestre, sequence=sequence, deleted_at__isnull=True
                ).aggregate(avg=models.Avg('valeur'))['avg'] or 0
                averages['by_sequence'].setdefault(trimestre, {})[sequence] = round(avg_sequence, 2)
        averages_by_student[student] = averages

    context = {
        'assigned_class': assigned_class,
        'students': students,
        'total_students': total_students,
        'subjects': subjects,
        'notes_by_student': notes_by_student,
        'averages_by_student': averages_by_student,
        'title': _('Teacher Dashboard'),
    }
    return render(request, 'enseignant/dashboard.html', context)

class NoteCreateView(CreateView):
    """View to add a note for a student."""
    model = Note
    form_class = NoteForm
    template_name = 'enseignant/note_form.html'
    success_url = reverse_lazy('schoolcopal:enseignant_dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = Enseignant.objects.get(user_id=self.request.user.id)
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _('Note added successfully.'))
        return super().form_valid(form)

class NoteUpdateView(UpdateView):
    """View to update a note for a student."""
    model = Note
    form_class = NoteForm
    template_name = 'enseignant/note_form.html'
    success_url = reverse_lazy('schoolcopal:enseignant_dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['teacher'] = Enseignant.objects.get(user_id=self.request.user.id)
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, _('Note updated successfully.'))
        return super().form_valid(form)

class NoteDeleteView(DeleteView):
    """View to delete a note for a student."""
    model = Note
    template_name = 'enseignant/note_confirm_delete.html'
    success_url = reverse_lazy('schoolcopal:enseignant_dashboard')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, _('Note deleted successfully.'))
        return redirect(self.success_url)