from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from manual_class_logging.signals import class_marked_as_used, class_renewed
from teachers.models import Teacher


"""
Method to mark purcased classes and subscriptions as used
"""


class MarkAsUsedForm(ActionForm):
    """
    Form for actions that is required to make following actions working
    """
    teacher = forms.ChoiceField(initial=-1, choices=Teacher.objects.can_finish_classes)


def write_log_entry(request, object, action_flag=admin.models.CHANGE, change_message='Changed'):
    entry = admin.models.LogEntry(
        user=request.user,
        object_id=object.pk,
        content_type=ContentType.objects.get_for_model(object),  # move it away from this function if you experience problems
        object_repr=str(object),
        action_flag=action_flag,
        change_message=change_message,
    )
    entry.save()


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
