from collections import OrderedDict

from crm.models import Customer
from elk.utils.testing import ClientTestCase


class TestGreetingsSmoke(ClientTestCase):
    def test_all_available_greetings(self):
        """
        Check if all greeting types has templates for the homepage
        """
        greetings = OrderedDict(Customer.GREETINGS)
        for greeting_type in greetings.keys():
            response = self.c.get('/?greeting=%s' % greeting_type)
            self.assertEqual(response.status_code, 200)
