from django.conf.urls import url

from . import views

urlpatterns = [
    url(regex=r'(?P<username>.+)/(?P<pk>\d+)/card/$',  # teacher username is ignored here for URL consistency
        view=views.TimelineEntryCardView.as_view(),
        name='entry_card',
        ),
    url(regex=r'(?P<username>.+)/(?P<pk>\d+)/delete_customer/(?P<customer>\d+)/$',
        view=views.delete_customer,
        name='delete_customer',
        ),
    url(regex=r'(?P<username>.+)/(?P<pk>\d+)/add_customer/(?P<customer>\d+)/$',
        view=views.add_customer,
        name='add_customer',
        ),

    url(regex=r'(?P<username>.+)/add/$',
        view=views.EntryCreate.as_view(),
        name='timeline_create',
        ),
    url(regex=r'(?P<username>.+)/(?P<pk>\d+)/$',
        view=views.EntryUpdate.as_view(),
        name='timeline_update',
        ),
    url(regex=r'(?P<username>.+)/(?P<pk>\d+)/delete/$',
        view=views.EntryDelete.as_view(),
        name='timeline_delete',
        ),

    url(regex=r'(?P<username>.+)/check_entry/(?P<start>[\d\:\ \-]+)/(?P<end>[\d\:\ \-]+)/$',
        view=views.check_entry,
        name='check_entry',
        ),

    url(r'(?P<username>.+)/$', views.TeacherCalendar.as_view(), name='timeline'),
]
