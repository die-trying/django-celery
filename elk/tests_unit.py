from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from django.apps import apps
from django.utils.dateformat import format
from django.utils.dateparse import parse_date

import elk.templatetags.custom_humanize as humanize
from elk.utils.date import ago, day_range, fwd
from elk.utils.testing import TestCase, create_customer, create_teacher, create_user


class TestDateUtils(TestCase):
    def test_ago(self):
        d = parse_date('2014-03-29')
        self.assertEqual(ago(d, days=29), '2014-02-28')
        self.assertEqual(ago(d, days=29, fmt='m/d/Y'), '02/28/2014')

        self.assertEqual(ago(days=16), format(datetime.now() - timedelta(days=16), 'Y-m-d'))

    def test_fwd(self):
        d = parse_date('2014-02-28')
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
    def test_create_user(self):
        User = apps.get_model('auth.user')
        user = create_user()
        self.assertEquals(User.objects.get(username=user.username), user)
        self.assertIsNotNone(user.crm)

    def test_create_customer(self):
        Customer = apps.get_model('crm.customer')
        customer = create_customer()

        self.assertEquals(Customer.objects.get(user__username=customer.user.username), customer)

    def test_create_teacher(self):
        Teacher = apps.get_model('teachers.teacher')
        teacher = create_teacher()

        t = Teacher.objects.get(user__username=teacher.user.username)
        self.assertEqual(t, teacher)
        self.assertIsNotNone(t.user.crm)
        self.assertTrue(t.user.is_staff)

    def test_create_teacher_all_lessons(self):
        teacher = create_teacher()
        allowed_lessons = teacher.allowed_lessons.all()
        self.assertGreater(allowed_lessons.count(), 0)
        self.assertEqual(allowed_lessons[0].app_label, 'lessons')


class TestTemplateTags(TestCase):
    def test_naturaltime_stripping(self):
        with patch('elk.templatetags.custom_humanize.humanize') as mocked_humanize:  # patching stock django 'humanize'
            mocked_humanize.naturaltime = MagicMock(return_value='some staff from now')
            result = humanize.naturaltime(100500)
            self.assertEqual(result, 'some staff')
