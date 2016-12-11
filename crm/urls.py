from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from crm import views

urlpatterns = [
    url('^issue/$', login_required(views.IssueCreate.as_view()), name='issue_create'),
    url(r'^mailchimp_csv/(?P<ids>[\d,]+)$', views.mailchimp_csv, name='mailchimp_csv'),
    url(r'^export_last_lessons/(?P<customers>[\d,]+)/start/(?P<start>[\d-]+)/end/(?P<end>[\d-]+)/$', views.export_last_lessons, name='export_last_lessons'),
]
