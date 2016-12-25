"""
Tiny fixture helper to generate `mixer<https://github.com/klen/mixer>`_-based
fixtures with correct relations.

Every new call returnes a new fixture.


TODO: move create_* functions to separate factory class
"""
import random
from datetime import datetime
from unittest.mock import Mock, patch

import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase as StockTestCase
from django.test import Client, RequestFactory
from django.utils import timezone
from mixer.backend.django import mixer
from rest_framework.test import APIClient
from with_asserts.mixin import AssertHTMLMixin

from lessons import models as lessons
from market.models import Class
from market.sortinghat import SortingHat
from timeline.models import Entry as TimelineEntry


def __add_all_lessons(teacher):
    for lesson in ContentType.objects.filter(app_label='lessons'):
        teacher.allowed_lessons.add(lesson)


def __add_working_hours_24x7(teacher):
    for weekday in range(0, 7):
        teacher.working_hours.create(
            weekday=weekday,
            start='00:00',
            end='23:59',
        )


def create_user(**kwargs):
    """
    Generate a simple user object.

    You can pass `mixer<https://github.com/klen/mixer>` keyword arguments for :model:`crm.Customer`
    or 'password' argument if you want to log in with this user
    """
    user = mixer.blend('auth.user')

    if kwargs.get('password'):
        user.set_password(kwargs.pop('password'))
        user.save()

    user.crm = create_customer(user=user, **kwargs)

    return user


def create_customer(user=None, **kwargs):
    """
    Generate a simple customer object.
    """
    if user is None:
        user = create_user(**kwargs)
    else:
        kwargs['timezone'] = kwargs.get('timezone', 'Europe/Moscow')  # the timezone value here deffers from default one in settings.py for early timezone error detection
        mixer.blend('crm.customer', user=user, **kwargs)

    return user.crm


def create_teacher(accepts_all_lessons=True, works_24x7=False):
    """
    Generate a simple teacher object.
    """
    customer = create_customer()
    teacher = mixer.blend('teachers.teacher', user=customer.user, teacher_photo=mixer.RANDOM)  # second level relations — that is wy i've created this helper
    teacher.user.is_staff = True
    teacher.user.save()

    if accepts_all_lessons:
        __add_all_lessons(teacher)

    if works_24x7:
        __add_working_hours_24x7(teacher)

    return teacher


def mock_request(customer=None):
    """
    Mock a request object, typicaly used for tests when buying a class
    """

    request = Mock()
    request.user_agent.is_mobile = bool(random.getrandbits(1))
    request.user_agent.is_tablet = bool(random.getrandbits(1))
    request.user_agent.is_pc = bool(random.getrandbits(1))

    request.user_agent.browser.family = 'Mobile Safari'
    request.user_agent.browser.version_string = '5.2'

    request.user_agent.os.family = 'WinXP'
    request.user_agent.os.version_string = '5.3'
    request.user_agent.device.family = 'iPhone'

    request.META = {
        'REMOTE_ADDR': '127.0.0.5',
        'HTTP_USER_AGENT': 'WinXP; U/16',
    }

    if customer is None:
        customer = create_customer()

    request.crm = customer

    return request


class TestCase(StockTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """
        Here we reset the timezone, which might be set by mistake inside any other test suite.
        the timezone support for web requests will work as expected, because
        of middleware elk.middleware.TimezoneMiddleware
        """
        timezone.deactivate()

    def assertIsTime(self, time):
        """
        Check if passed argument looks like a time definition
        """
        return self.assertRegexpMatches(str(time), r'\d{2}\:\d{2}')

    def assertRedirectsPartial(self, response, expected_url):
        """
        Check if response is a redirect and redirect URL contains expected_url
        """
        self.assertIn(response.status_code, [302, 301])
        self.assertIn(expected_url, response.url)

    @classmethod
    def tzdatetime(cls, *args, **kwargs):
        """
        Create a timezoned datetime
        """
        if isinstance(args[0], int):
            tz = settings.TIME_ZONE
        else:
            tz = args[0]
            args = args[1:]

        tz = pytz.timezone(tz)
        return timezone.make_aware(
            datetime(*args, **kwargs),
            timezone=tz,
        )


class SuperUserTestCaseMixin():
    @classmethod
    def _generate_superuser(cls):
        cls.superuser = User.objects.create_superuser('root', 'root@wheel.com', 'ohGh7jai4Cee')
        create_customer(user=cls.superuser)
        cls.superuser_login = 'root'
        cls.superuser_password = 'ohGh7jai4Cee'  # store, if children will need it

    @classmethod
    def _login(cls):
        cls.c.login(username=cls.superuser_login, password=cls.superuser_password)


class ClientTestCase(TestCase, SuperUserTestCaseMixin, AssertHTMLMixin):
    """
    Generic test case with automatic login process and all required assets.

    - Composes a django.test.RequestFactory and django.test.Client.
    - Creates a superuser (to avoid permission issues) and logges in with it's credetinals.

    For examples lurk the working tests.
    """

    fixtures = ('lessons', 'products')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.c = Client()
        cls.factory = RequestFactory()

        cls._generate_superuser()
        cls._login()


class APITestCase(TestCase, SuperUserTestCaseMixin):
    """
    Generic Test Case for API, using Django REST Framework test harness
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.c = APIClient()
        cls._generate_superuser()
        cls._login()


class ClassIntegrationTestCase(ClientTestCase):
    """
    TestCase for integration testing of scheduling process.

    Properties:
        — host: some random teacher
        - customer: some random customer
        - lesson: ordinay lesson

    Methods:
        - _create_entry() — create a timeline entry for the teacher
        - _buy_a_lesson() — buy a lesson for student
        - schedule() — schedule a user's lesson to the teachers entry
    """

    def setUp(self):
        self.host = create_teacher(accepts_all_lessons=True, works_24x7=True)
        self.customer = create_customer()
        self.lesson = lessons.OrdinaryLesson.get_default()

    @patch('timeline.models.Entry.clean')
    def _create_entry(self, clean):
        entry = TimelineEntry(
            slots=1,
            lesson=self.lesson,
            teacher=self.host,
            start=self.tzdatetime(2032, 9, 13, 12, 0),
        )
        self.assertFalse(entry.is_finished)
        return entry

    def _buy_a_lesson(self):
        c = Class(
            customer=self.customer,
            lesson_type=self.lesson.get_contenttype(),
        )
        c.save()
        self.assertFalse(c.is_fully_used)
        self.assertFalse(c.is_scheduled)
        return c

    @patch('timeline.models.Entry.clean')
    def _schedule(self, c, entry, clean):
        """
        Schedule a class to given timeline entry.

        ACHTUNG: for class with non-hosted lessons the entry will be the new one,
        not the one you've supplied.
        """
        clean.return_value = True
        hat = SortingHat(
            customer=c.customer,
            lesson_type=self.lesson.get_contenttype().pk,
            teacher=entry.teacher,
            date=entry.start.strftime('%Y-%m-%d'),
            time=entry.start.strftime('%H:%M'),
        )
        if not hat.do_the_thing():
            self.assertFalse(True, "Cant schedule a lesson: %s" % hat.err)
        self.assertEqual(hat.c, c)
        hat.c.save()

        c.refresh_from_db()
