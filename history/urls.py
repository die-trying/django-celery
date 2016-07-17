from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    url(
        regex=r'^payments/$',
        view=login_required(TemplateView.as_view(template_name='history/payments.html')),
        name='payments'
    ),
]
