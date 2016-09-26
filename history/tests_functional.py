from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from with_asserts.mixin import AssertHTMLMixin

from crm.models import Customer
from elk.utils.testing import mock_request
from lessons.models import OrdinaryLesson
from market.models import Class

from . import views


class TestEvent(TestCase, AssertHTMLMixin):
    """
    Buy a lesson, then fetch payments history — should see a record in the table
    """
    fixtures = ('lessons',)

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user('user', 'user@me.com', '123')
        self.user.first_name = 'Vasiliy'
        self.user.last_name = 'Poupkine'
        customer = Customer()
        customer.save()
        self.user.crm = customer

    def test_single_lesson(self):
        c = Class(
            customer=self.user.crm,
            lesson=OrdinaryLesson.get_default(),
            buy_price=150
        )
        c.request = mock_request()
        c.save()

        request = self.factory.get('/history/payments/')
        request.user = self.user

        response = views.Payments.as_view()(request)  # Я УМЕЮ ФУНКУЦИОНАЛЬНО ПРОГРАММИРОВАТЬ
        response.render()

        with self.assertHTML(response, 'table.payments-history>tbody .payments-history__product-column') as purchased_products:
            self.assertEqual(len(purchased_products), 1)
            self.assertEqual(purchased_products[0].text, OrdinaryLesson.get_default().name)
