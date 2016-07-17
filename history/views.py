from django.views.generic import TemplateView


class Payments(TemplateView):
    template_name = 'history/payments.html'
