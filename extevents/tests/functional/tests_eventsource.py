from django.contrib.contenttypes.models import ContentType
from mixer.backend.django import mixer

import extevents.models as models
from elk.utils.testing import create_teacher
from extevents.tests import GoogleCalendarTestCase


class TestEventSource(GoogleCalendarTestCase):
    """
    This complex suite contains tests for two sticked-together models:
    :model:`extevent.ExternalEvent' and :model:`extevent.ExternalEventSource`
    """
    def setUp(self):
        """
        Generate 10 random events in self.events
        """
        super().setUp()
        for i in range(0, 10):
            self.src.events.append(mixer.blend(
                models.ExternalEvent,
                teacher=self.teacher,
                ext_src=ContentType.objects.get_for_model(self.src)
            ))

    def tearDown(self):
        models.ExternalEvent.objects.all().delete()

    def test_generic_event_saving(self):
        def test_save(self):
            start = self.tzdatetime('Europe/Moscow', 2016, 12, 1, 12, 50)
            end = self.tzdatetime('Europe/Moscow', 2016, 12, 1, 12, 59)
            event = models.ExternalEvent(
                teacher=create_teacher(),
                start=start,
                end=end,
                description='testdescr',
                ext_src=ContentType.objects.get_for_model(models.GoogleCalendar)
            )
            event.save()
            self.assertIsNotNone(event.pk)

    def test_previous_event_cleanup(self):
        self.assertEqual(models.ExternalEvent.objects.count(), 10)
        self.src._ExternalEventSource__clear_previous_events()
        self.assertEqual(models.ExternalEvent.objects.count(), 0)  # all generated events should be deleted now

    def test_preserving_other_teachers_when_cleaning_previous_events(self):
        some_other_teacher = create_teacher()
        for i in range(0, 10):
            mixer.blend(
                models.ExternalEvent,
                teacher=some_other_teacher, ext_src=ContentType.objects.get_for_model(self.src)
            )

        self.assertEqual(models.ExternalEvent.objects.count(), 20)
        self.src._ExternalEventSource__clear_previous_events()
        self.assertEqual(models.ExternalEvent.objects.count(), 10)  # only events for self.teacher should be deleted
        self.assertEqual(models.ExternalEvent.objects.all()[0].teacher, some_other_teacher)  # events for some_other_teacher should not be touched

    def test_event_update(self):
        """
            1. Create 8 events, store it in the database
            2. Call update() to save fixtured events, generated in the self.setUp()
            3. Check if 8 events are deleted
        """
        for i in range(0, 8):
            mixer.blend(
                models.ExternalEvent,
                teacher=self.teacher, ext_src=ContentType.objects.get_for_model(self.src)
            )
        self.assertEqual(models.ExternalEvent.objects.count(), 18)  # 10 from self.src.events and 8 from now

        self.src.update()

        stored_events = models.ExternalEvent.objects.all()
        self.assertEqual(stored_events.count(), 10)

        c = 0
        for ev in stored_events:
            self.assertEqual(ev.start, self.src.events[c].start)
            self.assertEqual(ev.end, self.src.events[c].end)

            c += 1
