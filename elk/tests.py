from datetime import datetime, timedelta

import iso8601
from django.test import TestCase
from django.utils.dateformat import format

from elk.utils.date import ago, fwd


class TstDateUtils(TestCase):
    def test_ago(self):
        d = iso8601.parse_date('2014-03-29')
        self.assertEqual(ago(d, days=29), '2014-02-28')
        self.assertEqual(ago(d, days=29, fmt='m/d/Y'), '02/28/2014')

        self.assertEqual(ago(days=16), format(datetime.now() - timedelta(days=16), 'Y-m-d'))

    def test_fwd(self):
        d = iso8601.parse_date('2014-02-28')
        self.assertEqual(fwd(d, days=29), '2014-03-29')
        self.assertEqual(fwd(d, days=29, fmt='m/d/Y'), '03/29/2014')

        self.assertEqual(fwd(days=16), format(datetime.now() + timedelta(days=16), 'Y-m-d'))
