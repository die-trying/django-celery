from datetime import datetime

from elk.utils.date import common_timezones, day_range
from elk.utils.testing import TestCase


class TestDateUtils(TestCase):
    def test_day_range(self):
        r = day_range('2016-02-28')
        self.assertEquals(r, ('2016-02-28 00:00:00', '2016-02-28 23:59:59'))

    def test_day_range_for_datetime(self):
        r = day_range(datetime(2016, 2, 28))
        self.assertEquals(r, ('2016-02-28 00:00:00', '2016-02-28 23:59:59'))

    def test_common_timezones(self):
        a = list(common_timezones())
        self.assertGreater(len(a), 32)
