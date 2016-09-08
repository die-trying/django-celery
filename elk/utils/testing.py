"""
Tiny fixture helper to generate `mixer<https://github.com/klen/mixer>`_-based
fixtures with correct relations.

Every new call returnes a new fixture.
"""
import random
from unittest.mock import Mock

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase as StockTestCase
from django.test import Client, RequestFactory
from django.utils import timezone
from mixer.backend.django import mixer
from with_asserts.mixin import AssertHTMLMixin


def __add_all_lessons(teacher):
    for lesson in ContentType.objects.filter(app_label='lessons'):
        teacher.allowed_lessons.add(lesson)


def create_user(**kwargs):
    """
    Generate a simple user object.

    You can pass `mixer<https://github.com/klen/mixer>` keyword arguments for :model:`crm.Customer`
    """
    user = mixer.blend('auth.user')
    user.crm = create_customer(user=user)

    return user


def create_customer(user=None, **kwargs):
    """
    Generate a simple customer object.
    """
    if user is None:
        user = create_user(**kwargs)
    else:
        kwargs['timezone'] = kwargs.get('timezone', 'Europe/Moscow')  # the timezone value here defferes from default one in settings.py for early timezone error detection
        mixer.blend('crm.customer', user=user, **kwargs)

    return user.crm


def create_teacher(accepts_all_lessons=True):
    """
    Generate a simple teacher object.
    """
    customer = create_customer()
    teacher = mixer.blend('teachers.teacher', user=customer.user)  # second level relations — that is wy i've created this helper
    teacher.user.is_staff = True
    teacher.user.save()

    if accepts_all_lessons:
        __add_all_lessons(teacher)

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


class ClientTestCase(TestCase, AssertHTMLMixin):
    """
    Generic test case with automatic login process and all required assets.

    - Composes a django.test.RequestFactory and django.test.Client.
    - Creates a superuser (to avoid permission issues) and logges in with it's credetinals.

    For examples lurk the working tests.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.c = Client()
        cls.factory = RequestFactory()

        cls.__generate_superuser()

    @classmethod
    def __generate_superuser(cls):
        cls.superuser = User.objects.create_superuser('root', 'root@wheel.com', 'ohGh7jai4Cee')
        create_customer(user=cls.superuser)
        cls.c.login(username='root', password='ohGh7jai4Cee')

        cls.superuser_login = 'root'
        cls.superuser_password = 'ohGh7jai4Cee'  # store, if children will need it
