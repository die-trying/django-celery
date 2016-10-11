from django.views.generic.base import TemplateView

from products.models import Product1, SimpleSubscription
from teachers.models import Teacher


class Homepage(TemplateView):
    template_name = 'acc/index.html'

    def get_context_data(self, **kwargs):
        product1 = Product1.objects.get(pk=1)
        simple_subscription = SimpleSubscription.objects.get(pk=1)

        print(product1.get_tier(country=self.request.user.crm.country).name)
        return {
            'product1': product1,
            'product1_tier': product1.get_tier(country=self.request.user.crm.country),
            'simple_subscription': simple_subscription,
            'simple_subscription_tier': simple_subscription.get_tier(country=self.request.user.crm.country),

            'faces': self._teacher_faces('Fedor', 'Amanda', 'Andrew'),
        }

    def _teacher_faces(self, *faces):
        """
        Faces are the username list
        """
        for i in faces:
            yield Teacher.objects.filter(user__username=i).first()
