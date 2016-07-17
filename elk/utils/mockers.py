import random
from unittest.mock import Mock

from crm.models import Customer
from mixer.backend.django import mixer


def mock_request(customer=mixer.blend(Customer)):
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
    request.get_host = Mock(return_value='127.0.0.5')
    request.crm = customer

    return request
