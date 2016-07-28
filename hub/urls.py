from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^buy-single$', views.single, name='buy_a_single'),
    url(r'^buy-subscription$', views.subscription, name='buy_a_subscription'),
    url(regex=r'schedule/step2/(?P<teacher>\d+)/type/(?P<type_id>\d+)/(?P<date>[\d-]+)/(?P<time>[\d:]{5})/',
        view=views.step2_by_type,
        name='step2_by_type'
        ),
    url(regex=r'/schedule/step2/(?P<teacher>\d+)/entry/(?P<entry_id>\d+)/',
        view=views.step2_by_entry,
        name='step2_by_entry'
        ),
    url(regex=r'schedule/step1/',
        view=views.step1,
        name='step01'
        ),
]
