from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^payments$', login_required(TemplateView.as_view(template_name='payments.html')), name='payments'),
]
