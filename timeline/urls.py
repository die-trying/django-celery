from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from . import views

urlpatterns = [
    url(regex=r'(?P<username>.+)/create/$',
        view=staff_member_required(views.calendar_create.as_view()),
        name='timeline_create',
        ),
    url(regex=r'(?P<username>.+)/(?P<pk>\d+)/update/$',
        view=staff_member_required(views.calendar_update.as_view()),
        name='timeline_update',
        ),
    url(regex=r'(?P<username>.+)/(?P<pk>\d+)/delete/$',
        view=views.calendar_delete,
        name='timeline_delete',
        ),
    url(regex=r'(?P<username>.+)/check_overlap/(?P<start>[\d\:\ \-]+)/(?P<end>[\d\:\ \-]+)/$',
        view=views.check_overlap,
        name='check_overlap',
        ),
    url(r'(?P<username>.+).json', views.calendar_json, name='timeline.json'),
    url(r'(?P<username>.+)/$', views.calendar, name='timeline'),
]
