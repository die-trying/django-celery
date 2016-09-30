from django.template import Context, Template
from django.test import override_settings

from elk.utils.testing import TestCase


class TestAbsoluteUrlGenerator(TestCase):
    TEMPLATE = Template("{% load absolute_url %} {% absolute_url 'timeline:entry_card' username='user' pk=100500 %}")

    @override_settings(ABSOLUTE_HOST='https://a.app')
    def test_host_appending(self):
        rendered = self.TEMPLATE.render(Context({}))
        self.assertIn('https://a.app/timeline/user/100500/card/', rendered)
