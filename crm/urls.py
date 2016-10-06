from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from crm import views

urlpatterns = [
    url('^issue/$', login_required(views.IssueCreate.as_view()), name='issue_create'),
]
