from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from crm import views

urlpatterns = [
    url('^issue/$', login_required(views.IssueCreate.as_view()), name='issue_create'),
    url(r'^mailchimp_csv/(?P<ids>[\d,]+)$', views.mailchimp_csv, name='mailchimp_csv'),
]
