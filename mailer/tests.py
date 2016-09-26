import pytz
from django.utils import timezone

from elk.utils.testing import TestCase
from mailer.owl import Owl


class TestTemplatedMail(TestCase):
    def _ctx(self):
        return {
            'username': 'abraham.lincoln',
            'full_name': 'Abraham Lincoln',
            'register_date': '12.09.1809',
            'time': self.tzdatetime('Europe/Moscow', 2016, 9, 26, 19, 0),
        }

    def _owl(self, **kwargs):
        return Owl(
            template='mailer/test.html',
            ctx=self._ctx(),
            to=['f@f213.in'],
            **kwargs
        )

    def test_subject(self):
        owl = self._owl()
        owl.send()
        m = owl.msg
        self.assertIn('сабжекта для abraham.lincoln', m.subject)

    def test_body(self):
        owl = self._owl()
        owl.send()
        m = owl.msg
        self.assertIn('Abraham Lincoln', m.body)
        self.assertIn('12.09.1809', m.body)
        self.assertIn('abraham.lincoln', m.body)

    def test_timezone_str(self):
        """
        Pass a timezone, in which letter should be composed
        """
        timezone.activate('US/Eastern')
        owl = self._owl(timezone='Europe/Amsterdam')
        owl.send()
        m = owl.msg
        self.assertIn('26.09.2016 18:00', m.body)

        self.assertEqual(timezone.get_current_timezone_name(), 'US/Eastern')  # timezone should be restored

    def test_timezone_pytz(self):
        """
        Pass a pytz instance for the optional timezone arg
        """
        timezone.activate('US/Eastern')
        owl = self._owl(timezone=pytz.timezone('Europe/Amsterdam'))
        owl.send()
        m = owl.msg
        self.assertIn('26.09.2016 18:00', m.body)
