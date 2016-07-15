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
        view=staff_member_required(views.calendar_delete),
        name='timeline_delete',
        ),
    url(r'(?P<username>.+)/available_lessons.json$', views.available_lessons_json, name='available_lessons_json'),
    url(r'(?P<username>.+).json', views.calendar_json, name='timeline.json'),
    url(r'(?P<username>.+)/$', views.calendar, name='timeline'),
]
