"""
Tiny fixture helper to generate `mixer<https://github.com/klen/mixer>`_-based
fixtures with correct relations.

Every new call returnes a new fixture.
"""
import random
from unittest.mock import Mock

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, RequestFactory, TestCase
from mixer.backend.django import mixer
from with_asserts.mixin import AssertHTMLMixin


def __add_all_lessons(teacher):
    for lesson in ContentType.objects.filter(app_label='lessons'):
        teacher.acceptable_lessons.add(lesson)


def create_user():
    """
    Generate a simple user object.
    """
    user = mixer.blend('auth.user')
    mixer.blend('crm.customer', user=user)
    return user


def create_customer():
    """
    Generate a simple customer object.
    """
    user = create_user()
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


def mock_request(customer=create_customer()):
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
    request.crm = customer

    return request


class ClientTestCase(TestCase, AssertHTMLMixin):
    """
    Generic test case with automatic login process and all required assets.

    Composes a django.test.RequestFactory and django.test.Client. Creates a superuser
    (to avoid permission issues) and logges in with it's credetinals.

    For examples lurk the working tests.
    """
    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()
        self.superuser = User.objects.create_superuser('root', 'root@wheel.com', 'ohGh7jai4Cee')
        self.c.login(username='root', password='ohGh7jai4Cee')

        self.superuser_login = 'root'
        self.superuser_password = 'ohGh7jai4Cee'  # store, if children will need it
