from django.test import TestCase

from mailer.owl import Owl


class TestTemplatedMail(TestCase):
    def _ctx(self):
        return {
            'username': 'abraham.lincoln',
            'full_name': 'Abraham Lincoln',
            'register_date': '12.09.1809'
        }

    def test_subject(self):
        owl = Owl(
            template='mailer/test.html',
            ctx=self._ctx(),
            to=['f@f213.in']
        )
        owl.send()
        m = owl.msg
        self.assertIn('сабжекта для abraham.lincoln', m.subject)

    def test_body(self):
        owl = Owl(
            template='mailer/test.html',
            ctx=self._ctx(),
            to=['f@f213.in'],
        )
        owl.send()
        m = owl.msg
        self.assertIn('Abraham Lincoln', m.body)
        self.assertIn('12.09.1809', m.body)
        self.assertIn('abraham.lincoln', m.body)
