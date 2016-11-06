from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer, create_teacher
from lessons import models as lessons
from market.models import Class
from timeline.models import Entry as TimelineEntry


class TestCancellation(TestCase):
    """
    Actions with timeline entries with attached classes should
    influence the classes too, and vice-versa
    """
    fixtures = ('lessons',)

    def setUp(self):
        self.teacher = create_teacher(works_24x7=True)
        self.customer = create_customer()
        self.lesson = mixer.blend(lessons.MasterClass, host=self.teacher, slots=15)

    def _buy_a_lesson(self, lesson):
        c = Class(
            customer=self.customer,
            lesson_type=lesson.get_contenttype(),
        )
        c.save()
        return c

    def _create_entry(self, start=datetime(2032, 5, 3, 13, 30), end=datetime(2032, 5, 3, 14, 0)):
        if timezone.is_naive(start):
            start = timezone.make_aware(start)
        if timezone.is_naive(end):
            end = timezone.make_aware(end)

        return mixer.blend(
            TimelineEntry,
            teacher=self.teacher,
            lesson=self.lesson,
            start=start,
            end=end,
        )

    def test_cancel_entry(self):
        """
        When deleting a timeline entry, the class should become unscheduled.
        """
        c = self._buy_a_lesson(self.lesson)
        entry = self._create_entry()
        c.assign_entry(entry)
        c.save()

        self.assertTrue(c.is_scheduled)

        entry = TimelineEntry.objects.get(pk=entry.id)
        entry.delete()
        c.refresh_from_db()
        self.assertFalse(c.is_scheduled)

    def test_entry_autodelete(self):
        """
        Entry without taken slots with a lesson, that does not require an entry should delete itself.
        """
        lesson = mixer.blend(lessons.OrdinaryLesson)  # blend a lesson, that does not require a timeline entry
        c = self._buy_a_lesson(lesson)
        c.schedule(  # go through the simple scheduling process, without a special-crafted timeline entry
            teacher=self.teacher,
            date=self.tzdatetime(2032, 5, 3, 12, 30),
        )
        c.save()
        entry = c.timeline
        self.assertIsInstance(entry, TimelineEntry)
        c.delete()
        self.assertFalse(TimelineEntry.objects.filter(pk=entry.pk).exists())  # during the class saving, entry should have deleted itself

    def test_entry_no_autodelete_on_lessons_that_require_a_timeline_entry(self):
        """
        Timeline entries for lessons, that require it, should not be deleted event when the class cancles.

        The difference with the previous test is that we buy a master class,
        which requires a timeline entry.
        """
        c = self._buy_a_lesson(self.lesson)  # self.lesson is a master class, so it requires an entry
        entry = self._create_entry()
        c.assign_entry(entry)
        c.save()
        entry = c.timeline
        self.assertIsInstance(entry, TimelineEntry)

        c.delete()
        self.assertTrue(TimelineEntry.objects.filter(pk=entry.pk).exists())  # auto-deletion mechanism should not be engaged

    def test_mark_classes_as_finished(self):
        """
        Assign ten classes to the entry and check if it marks them as fully used.

        This a functional test, but i have related fixtures (_create_entry(), _buy_a_lesson()),
        so it will wait until refactoring.
        """
        entry = self._create_entry()

        for i in range(0, 10):
            c = self._buy_a_lesson(self.lesson)
            c.is_fully_used = False
            c.save()

        for c in entry.classes.all():
            self.assertFalse(c.is_fully_used)

        entry.is_finished = True
        entry.save()

        for c in entry.classes.all():
            self.assertTrue(c.is_fully_used)

    def test_cancellation_of_a_non_hosted_lesson(self):
        """
        Special test case for cancelling the timeline entries for lessons, that don't
        require a timeline entry. The entry should delete itself and not throw any errors
        """
        self.lesson = mixer.blend(lessons.OrdinaryLesson)
        c = self._buy_a_lesson(lesson=self.lesson)
        entry = self._create_entry()
        c.assign_entry(entry)
        c.save()

        self.assertTrue(c.is_scheduled)

        entry = TimelineEntry.objects.get(pk=entry.id)

        entry.delete()  # should not thow anything

        c.refresh_from_db()
        self.assertFalse(c.is_scheduled)

        with self.assertRaises(ObjectDoesNotExist):
            entry.refresh_from_db()
