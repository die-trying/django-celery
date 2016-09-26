from mixer.backend.django import mixer

from extevents.models import ExternalEvent
from extevents.tests import GoogleCalendarTestCase


class TestExternalEventManager(GoogleCalendarTestCase):
    def test_by_src(self):
        for i in range(0, 10):
            mixer.blend(ExternalEvent, teacher=self.teacher, src=self.src)

        self.assertEqual(ExternalEvent.objects.by_src(self.src).count(), 10)
