from unittest.mock import MagicMock

from elk.geoip import GeoIP
from elk.utils.testing import TestCase


class TestGeoIp(TestCase):
    def test_init(self):
        g = GeoIP('71.192.161.223')
        self.assertIsNotNone(g._response)

    def test_properties(self):
        g = GeoIP('77.37.209.115')
        self.assertEqual(g.country, 'RU')
        self.assertEqual(g.city, 'Moscow')
        self.assertEqual(g.timezone, 'Europe/Moscow')
        self.assertEqual(g.lat, 55.752)
        self.assertEqual(g.lng, 37.615)

    def test_timezone_tzwhere(self):
        """
        When tz can't be determined by geolite, it should be guessed by coordinates
        """
        g = GeoIP('77.37.209.115')
        g._response.location = MagicMock()
        g._response.location.time_zone = None
        g._response.location.longitude = 37.61
        g._response.location.latitude = 55.75

        self.assertEqual(g.timezone, 'Europe/Moscow')
