import icalendar
from django.test import override_settings

from elk.utils.testing import TestCase
from mailer.ical import Ical


class TestIcal(TestCase):
    def setUp(self):
        self.ical = Ical(
            uid='123',
            start=self.tzdatetime(2032, 12, 5, 13, 30),
            end=self.tzdatetime(2032, 12, 5, 14, 0),
            summary='tst-smrr',
        )

    def test_event(self):
        ev = self.ical._event()
        self.assertEqual(ev['summary'], 'tst-smrr')
        self.assertEqual(ev['dtstart'].dt, self.tzdatetime(2032, 12, 5, 13, 30))
        self.assertEqual(ev['dtend'].dt, self.tzdatetime(2032, 12, 5, 14, 0))

    @override_settings(ABSOLUTE_HOST='https://tst100500.ru', SUPPORT_EMAIL='test@test.org')
    def test_event_boilerplate(self):
        ev = self.ical._event_boilerplate()
        self.assertEqual(ev['uid'], '123@tst100500.ru')
        self.assertIn('test@test.org', ev['ogranizer'].to_ical().decode())

    def test_calendar(self):
        c = icalendar.Calendar.from_ical(
            self.ical.as_string()
        )
        ev = c.walk('VEVENT')[0]

        self.assertIsNotNone(ev)
        self.assertEqual(ev['summary'], 'tst-smrr')

    def test_calendar_boilerplate(self):
        c = icalendar.Calendar.from_ical(
            self.ical.as_string()
        )
        self.assertIn('ELK', c['prodid'])
        self.assertIn('2.0', c['version'])
        self.assertIn('REQUEST', c['method'])

        alarm = c.walk('VALARM')[0]
        self.assertIn('DISPLAY', alarm.to_ical().decode())
