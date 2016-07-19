from datetime import datetime, timedelta

from django.apps import apps
from django.test import TestCase
from django.utils.dateformat import format

import iso8601
from elk.utils.date import ago, day_range, fwd
from elk.utils.test import test_customer, test_teacher, test_user


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

    def testDayRange(self):
        r = day_range('2016-02-28')
        self.assertEquals(r, ('2016-02-28 00:00:00', '2016-02-28 23:59:59'))


class TestFixtures(TestCase):
    """
    Test if my fixtures helper generates fixtures with correct relations
    """
    def test_user(self):
        User = apps.get_model('auth.user')
        user = test_user()
        self.assertEquals(User.objects.get(username=user.username), user)
        self.assertIsNotNone(user.crm)

    def test_customer(self):
        Customer = apps.get_model('crm.customer')
        customer = test_customer()

        self.assertEquals(Customer.objects.get(user__username=customer.user.username), customer)

    def test_teacher(self):
        Teacher = apps.get_model('teachers.teacher')
        teacher = test_teacher()

        t = Teacher.objects.get(user__username=teacher.user.username)
        self.assertEqual(t, teacher)
        self.assertIsNotNone(t.user.crm)
        self.assertTrue(t.user.is_staff)

    def test_teacher_all_lessons(self):
        teacher = test_teacher()
        acceptable_lessons = teacher.acceptable_lessons.all()
        self.assertGreater(acceptable_lessons.count(), 0)
        self.assertEqual(acceptable_lessons[0].app_label, 'lessons')
