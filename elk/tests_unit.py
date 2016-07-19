from datetime import datetime, timedelta

import iso8601
from django.apps import apps
from django.test import TestCase
from django.utils.dateformat import format

from elk.utils.date import ago, fwd
from elk.utils.fixtures import test_customer, test_teacher


class TestDateUtils(TestCase):
    def test_ago(self):
        d = iso8601.parse_date('2014-03-29')
        self.assertEqual(ago(d, days=29), '2014-02-28')
        self.assertEqual(ago(d, days=29, fmt='m/d/Y'), '02/28/2014')

        self.assertEqual(ago(days=16), format(datetime.now() - timedelta(days=16), 'Y-m-d'))

    def test_fwd(self):
        d = iso8601.parse_date('2014-02-28')
        self.assertEqual(fwd(d, days=29), '2014-03-29')
        self.assertEqual(fwd(d, days=29, fmt='m/d/Y'), '03/29/2014')

        self.assertEqual(fwd(days=16), format(datetime.now() + timedelta(days=16), 'Y-m-d'))


class TestFixtures(TestCase):
    """
    Test if my fixtures helper generates fixtures with correct relations
    """
    def test_customer(self):
        Customer = apps.get_model('crm.customer')
        customer = test_customer()

        self.assertEquals(Customer.objects.get(user__username=customer.user.username), customer)

    def test_teacher(self):
        Teacher = apps.get_model('teachers.teacher')
        teacher = test_teacher()

        t = Teacher.objects.get(user__username=teacher.user.username)
        self.assertEquals(t, teacher)
        self.assertIsNotNone(t.user.crm)
