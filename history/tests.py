import random
from unittest.mock import Mock

from django.test import TestCase

from history.models import PaymentEvent


# Create your tests here.

class TestEvent(TestCase):
    def setUp(self):
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
            'HTTP_HOST': '127.0.0.5',
            'HTTP_USER_AGENT': 'WinXP; U/16',
        }
        self.request = request

    def testStoreRequest(self):
        ev = PaymentEvent()
        ev.store_request(self.request)

        self.assertEqual(ev.is_mobile, self.request.user_agent.is_mobile)
        self.assertEqual(ev.is_tablet, self.request.user_agent.is_tablet)
        self.assertEqual(ev.is_pc, self.request.user_agent.is_pc)

        self.assertEqual(ev.browser_family, 'Mobile Safari')
        self.assertEqual(ev.browser_version, '5.2')
        self.assertEqual(ev.os_family, 'WinXP')
        self.assertEqual(ev.os_version, '5.3')
        self.assertEqual(ev.device, 'iPhone')

        self.assertEqual(ev.raw_useragent, 'WinXP; U/16')
        self.assertEqual(ev.ip, '127.0.0.5')
