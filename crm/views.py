import csv

from django.apps import apps
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.formats import date_format
from django.views.generic.edit import CreateView

from crm.models import Issue
from elk.utils.forms import AjaxResponseMixin


class IssueCreate(AjaxResponseMixin, CreateView):
    model = Issue
    fields = ['body']

    def form_valid(self, form):
        issue = form.save(commit=False)
        issue.customer = self.request.user.crm

        return super().form_valid(form)


@permission_required('crm.change_customer')
def mailchimp_csv(request, ids):
    ids = ids.split(',')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dashboard-mailchimp.csv"'

    writer = csv.writer(response)

    writer.writerow(['Email', 'First name', 'Last name'])

    for user in User.objects.filter(crm__id__in=ids).values_list('email', 'first_name', 'last_name'):
        if not len(user[0]):  # if there is no email
            continue
        writer.writerow(user)

    return response


@permission_required('crm.change_customer')
def export_last_lessons(request, customers, start, end):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="last-lessons.csv"'
    writer = csv.writer(response, delimiter="\t")
    writer.writerow(['Date', 'Student(s)', 'Teacher', 'Lesson type'])

    customers = customers.split(',')
    TimelineEntry = apps.get_model('timeline.Entry')

    for entry in TimelineEntry.objects.filter(
        start__range=(start, end),
        classes__customer__in=customers,
        is_finished=True,
    ).distinct().order_by('start'):
        students = ', '.join(str(i.customer) for i in entry.classes.all())
        writer.writerow([
            date_format(entry.start, format='SHORT_DATETIME_FORMAT'),
            students,
            entry.teacher.user.crm.full_name,
            entry.lesson_type,
        ])

    return response
