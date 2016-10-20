from datetime import timedelta

from icalendar import Calendar
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_teacher
from lessons import models as lessons
from timeline.models import Entry as TimelineEntry


class TestTimelineIcal(TestCase):
    def setUp(self):
        self.teacher = create_teacher()
        self.lesson = mixer.blend(lessons.MasterClass, host=self.teacher, duration=timedelta(minutes=33), slots=8)

        self.entry = mixer.blend(
            TimelineEntry,
            teacher=self.teacher,
            lesson=self.lesson,
            start=self.tzdatetime(2032, 12, 1, 15, 0)
        )

    def test_ical(self):
        ical = Calendar.from_ical(self.entry._ical('test title'))
        ev = ical.walk('VEVENT')[0]
        self.assertEqual(ev['dtstart'].dt, self.tzdatetime(2032, 12, 1, 15, 0))
        self.assertEqual(ev['dtend'].dt, self.tzdatetime(2032, 12, 1, 15, 33))
        self.assertEqual(ev['summary'], 'test title')

    def test_ical_timezone(self):
        self.entry.start = self.tzdatetime('Asia/Vladivostok', 2032, 12, 1, 15, 0)
        self.entry.save()

        ical = Calendar.from_ical(self.entry._ical('test title'))
        ev = ical.walk('VEVENT')[0]

        self.assertEqual(ev['dtstart'].dt, self.tzdatetime('Asia/Vladivostok', 2032, 12, 1, 15, 0))
        self.assertEqual(ev['dtend'].dt, self.tzdatetime('Asia/Vladivostok', 2032, 12, 1, 15, 33))
