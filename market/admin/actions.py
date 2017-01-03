from django import forms
from django.contrib import admin
from django.shortcuts import redirect

from elk.admin.forms import ActionFormWithParams
from elk.logging import write_admin_log_entry
from teachers.models import Teacher


"""
Method to mark purcased classes and subscriptions as used
"""


class MarkAsUsedForm(ActionFormWithParams):
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

    for c in queryset.all():
        if not c.is_fully_used:
            c.mark_as_fully_used()
            write_admin_log_entry(
                user=request.user,
                object=c,
                msg='Marked as used',
            )


def renew(modeladmin, request, queryset):
    """
    Admin action to mark classes as renewed
    """
    pk = int(request.POST['teacher'])

    # TODO: refactor it!
    if pk == -1:  # when no teacher is specified
        pk = request.user.teacher_data.pk

    for c in queryset.all():
        if c.is_fully_used:
            c.renew()
            write_admin_log_entry(
                user=request.user,
                object=c,
                msg='Renewed',
            )


def export_emails(modeladmin, request, queryset):
    """
    Export emails of customers for selected subscriptions
    """
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    customers = [str(customer) for customer in queryset.filter(pk__in=selected).values_list('customer__pk', flat=True)]

    return redirect('crm:mailchimp_csv', ids=','.join(customers))
