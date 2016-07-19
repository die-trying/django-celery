"""
Tiny fixture helper to generate `mixer<https://github.com/klen/mixer>`_-based
fixtures with correct relations.

Every new call returnes a new fixture.
"""
import random
from unittest.mock import Mock

from mixer.backend.django import mixer


def test_user():
    user = mixer.blend('auth.user')
    mixer.blend('crm.customer', user=user)
    return user


def test_customer():
    user = test_user()
    return user.crm


def test_teacher():
    customer = test_customer()
    return mixer.blend('teachers.teacher', user=customer.user)  # second level relations — that is wy i've created this helper


def mock_request(customer=test_customer()):
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
    request.get_host = Mock(return_value='127.0.0.5:8553')
    request.crm = customer

    return request
