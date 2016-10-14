import pytz
from django.core import mail
from django.test import override_settings
from django.utils import timezone
from freezegun import freeze_time

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

    @override_settings(EMAIL_ASYNC=False)
    def test_send(self):
        owl = self._owl()
        owl.send()
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(EMAIL_ASYNC=True, CELERY_ALWAYS_EAGER=True)
    def test_send_async(self):
        owl = self._owl()
        owl.send()
        self.assertEqual(len(mail.outbox), 1)

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

    def test_email_from(self):
        owl = self._owl(from_email='ttt@test.org')
        owl.send()
        m = owl.msg
        self.assertEqual(m.from_email, 'ttt@test.org')

    @override_settings(EMAIL_NOTIFICATIONS_FROM='ttt@test.org')
    def test_email_from_default(self):
        owl = self._owl()
        owl.send()
        m = owl.msg
        self.assertEqual(m.from_email, 'ttt@test.org')

    @override_settings(REPLY_TO='reply@to.to')
    def test_reply_to(self):
        owl = self._owl()
        owl.send()
        m = owl.msg
        self.assertIn('reply@to.to', m.reply_to)

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

    @override_settings(EMAIL_ASYNC=True, CELERY_ALWAYS_EAGER=True)
    def test_timezone_async(self):
        """
        Check timezone traversal through Celery
        """
        timezone.activate('US/Eastern')
        owl = self._owl(timezone=pytz.timezone('Europe/Amsterdam'))
        owl.send()
        m = owl.msg
        self.assertIn('26.09.2016 18:00', m.body)
        self.assertEqual(m.extra_headers['X-ELK-Queued'], 'True')

    def test_timezone_headers_none(self):
        owl = self._owl()
        owl.send()
        m = owl.msg
        self.assertEqual(m.extra_headers['X-ELK-Timezone'], 'None')

    def test_timezone_headers_set(self):
        owl = self._owl(timezone=pytz.timezone('Europe/Amsterdam'))
        owl.send()
        m = owl.msg
        self.assertEqual(m.extra_headers['X-ELK-Timezone'], 'Europe/Amsterdam')

    @freeze_time('2016-09-27 19:00')
    @override_settings(USE_I18N=True, LANGUAGE_CODE='ru')
    def test_l18n_is_disabled(self):
        owl = self._owl()
        self.assertIn('<dd>yesterday</dd>', owl.msg.body)  # should be 'yesterday', not 'вчера'
