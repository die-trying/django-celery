from django import forms
from django.contrib.admin.helpers import ActionForm
from django.shortcuts import get_object_or_404

from elk.admin import write_log_entry
from manual_class_logging.signals import class_marked_as_used, class_renewed
from teachers.models import Teacher


class MarkAsUsedForm(ActionForm):
    """
    Form for actions that is required to make following actions working
    """
    teacher = forms.ChoiceField(initial=-1, choices=Teacher.objects.can_finish_classes)


def mark_as_used(modeladmin, request, queryset):
    """
    Admin action to mark classes as fully used
    """
    pk = int(request.POST['teacher'])

    # TODO: refactor it!
    if pk == -1:  # when no teacher is specified
        pk = request.user.teacher_data.pk

    teacher = get_object_or_404(Teacher, pk=pk)

    for c in queryset.all():
        if not c.is_fully_used:
            c.mark_as_fully_used()
            write_log_entry(
                request=request,
                object=c,
                change_message='Marked as used',
            )
            class_marked_as_used.send(sender=mark_as_used, instance=c, teacher=teacher)


def renew(modeladmin, request, queryset):
    """
    Admin action to mark classes as renewed
    """
    pk = int(request.POST['teacher'])

    # TODO: refactor it!
    if pk == -1:  # when no teacher is specified
        pk = request.user.teacher_data.pk

    teacher = get_object_or_404(Teacher, pk=pk)

    for c in queryset.all():
        if c.is_fully_used:
            c.renew()
            write_log_entry(
                request=request,
                object=c,
                change_message='Renewed',
            )
            class_renewed.send(sender=renew, instance=c, teacher=teacher)
