from django.conf.urls import url

from . import views

urlpatterns = [
    url(regex=r'(?P<username>.+)/(?P<pk>\d+)/card/$',
        view=views.entry_card,
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


    url(regex=r'find_entry/(?P<teacher>.+)/(?P<lesson_type>\d+)/(?P<lesson_id>\d+)/(?P<start>.+)/',
        view=views.find_entry,
        name='find_entry',
        ),

    url(r'(?P<username>.+)/$', views.calendar, name='timeline'),
]
