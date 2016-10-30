import csv

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.http import HttpResponse
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
