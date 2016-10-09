from django.views.generic.base import TemplateView

from products.models import Product1, SimpleSubscription
from teachers.models import Teacher


class Homepage(TemplateView):
    template_name = 'acc/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['product1'] = Product1.objects.get(pk=1)
        ctx['simple_subscription'] = SimpleSubscription.objects.get(pk=1)

        ctx['faces'] = self._teacher_faces('Fedor', 'Amanda', 'Andrew')

        return ctx

    def _teacher_faces(self, *faces):
        """
        Faces are the username list
        """
        for i in faces:
            yield Teacher.objects.filter(user__username=i).first()
