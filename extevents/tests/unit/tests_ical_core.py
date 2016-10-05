import datetime

from icalendar.prop import vRecur

from elk.utils.testing import TestCase, create_teacher
from extevents.models import GoogleCalendar


class TestIcalGenericUtils(TestCase):
    def setUp(self):
        self.teacher = create_teacher()
        self.src = GoogleCalendar(
            teacher=self.teacher,
            url='http://testing'
        )

    def test_rrule_appends_timezone(self):
        rrule = vRecur(
            BYMONTHDAY=[3],
            FREQ=['MONTHLY'],
            UNTIL=[datetime.date(2016, 8, 31)]
        )

        s = self.src._build_generating_rule(rrule)
        self.assertIn('Z;', s)  # should contain a UTC identifier

    def test_rrule_does_not_append_timezone_when_it_is_set(self):
        rrule = vRecur(
            BYMONTHDAY=[3],
            FREQ=['MONTHLY'],
            UNTIL=[self.tzdatetime('UTC', 2016, 8, 31, 15, 0)]
        )
        s = self.src._build_generating_rule(rrule)
        self.assertIn('Z;', s)  # should contain a UTC identifier
