from datetime import datetime, timedelta

from django.utils.dateformat import format
from django.utils.dateparse import parse_date

from elk.utils.date import ago, day_range, fwd
from elk.utils.testing import TestCase


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

    def test_day_range(self):
        r = day_range('2016-02-28')
        self.assertEquals(r, ('2016-02-28 00:00:00', '2016-02-28 23:59:59'))
