from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(
        regex=r'^payments/$',
        view=login_required(views.Payments.as_view()),
        name='payments'
    ),
]
