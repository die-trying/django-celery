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
