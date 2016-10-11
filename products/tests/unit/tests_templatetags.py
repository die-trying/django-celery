from django.template import Context, Template

from elk.utils.testing import TestCase


class TestPaypal(TestCase):
    def test_buy_now(self):
        tpl = Template('{% load buy_now from paypal_buttons %} {% buy_now 100500 %}')
        html = tpl.render(Context({}))

        self.assertIn('100500', html)
        self.assertIn('hosted_button_id', html)
