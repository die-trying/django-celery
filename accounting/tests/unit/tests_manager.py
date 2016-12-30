from mixer.backend.django import mixer

from accounting.models import Event as AccEvent
from elk.utils.testing import TestCase, create_teacher
from timeline.models import Entry as TimelineEntry


class TestEventManager(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = create_teacher()

    def test_find_events_by_originator_ok(self):
        originator = mixer.blend(TimelineEntry, teacher=self.teacher)

        mixer.blend(AccEvent, originator=originator, teacher=self.teacher)

        found = AccEvent.objects.by_originator(originator)
        self.assertEqual(found.count(), 1)

    def test_find_events_by_originator_fail(self):
        originator1 = mixer.blend(TimelineEntry, teacher=self.teacher)
        originator2 = mixer.blend(TimelineEntry, teacher=self.teacher)

        mixer.blend(AccEvent, originator=originator1, teacher=self.teacher)

        found = AccEvent.objects.by_originator(originator2)
        self.assertEqual(found.count(), 0)
