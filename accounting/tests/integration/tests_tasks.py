from unittest.mock import patch

from mixer.backend.django import mixer

from accounting.models import Event as AccEvent
from accounting.tasks import bill_timeline_entries
from elk.utils.testing import TestCase, create_customer, create_teacher
from lessons import models as lessons
from market.models import Class
from market.sortinghat import SortingHat
from timeline.models import Entry as TimelineEntry


class TestClassIntegration(TestCase):
    """
    Big integration test:
        — Buy a lesson
        — Create a timeline entry for the teacher
        — Schedule this lesson
        — Wait until it's passed
        — ???
        — Check if entry is marked as finished
        — Check if class is marked as used
        — Check if billing event created
    """
    fixtures = ('lessons',)

    def setUp(self):
        self.host = create_teacher()
        self.customer = create_customer()
        self.lesson = lessons.OrdinaryLesson.get_default()

    def _buy_a_lesson(self):
        c = Class(
            customer=self.customer,
            lesson=self.lesson,
        )
        c.save()
        self.assertFalse(c.is_fully_used)
        self.assertFalse(c.is_scheduled)
        return c

    def _create_entry(self):
        entry = mixer.blend(
            TimelineEntry,
            slots=1,
            lesson=self.lesson,
            teacher=self.host,
            start=self.tzdatetime(2032, 9, 13, 12, 0),
        )
        self.assertFalse(entry.is_finished)
        return entry

    def _schedule(self, c, entry):
        hat = SortingHat(
            customer=c.customer,
            lesson_type=self.lesson.get_contenttype().pk,
            teacher=entry.teacher,
            date=entry.start.strftime('%Y-%m-%d'),
            time=entry.start.strftime('%H:%M'),
        )
        if not hat.do_the_thing():
            self.assertFalse(True, "Cant schedule a lesson!")
        self.assertEqual(hat.c, c)
        hat.c.save()

    @patch('timeline.models.EntryManager._EntryManager__now')
    def test_class_marked_as_used(self, now):
        c = self._buy_a_lesson()
        entry = self._create_entry()

        self._schedule(c, entry)

        c.refresh_from_db()
        self.assertTrue(c.is_scheduled)

        now.return_value = self.tzdatetime(2032, 9, 13, 15, 0)

        bill_timeline_entries()

        c.refresh_from_db()
        entry.refresh_from_db()

        self.assertTrue(entry.is_finished)
        self.assertTrue(c.is_fully_used)

        self.assertEqual(AccEvent.objects.count(), 1)
