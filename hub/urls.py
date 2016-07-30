from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^buy-single$', views.single, name='buy_a_single'),
    url(r'^buy-subscription$', views.subscription, name='buy_a_subscription'),
    url(regex=r'schedule/step2/teacher/(?P<teacher>\d+)/(?P<type_id>\d+)/(?P<date>[\d-]+)/(?P<time>[\d:]{5})/',
        view=views.step2,
        name='step2'
        ),
    url(regex=r'schedule/step1/',
        view=views.step1,
        name='step01'
        ),
]
