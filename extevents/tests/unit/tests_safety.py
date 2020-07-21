from unittest.mock import MagicMock, patch

from mixer.backend.django import Mixer, mixer

from extevents.models import ExternalEvent
from extevents.tests import GoogleCalendarTestCase


class TestEventSourceSafety(GoogleCalendarTestCase):
    def setUp(self):
        super().setUp()
        self.src.events = []
        self.safe_mixer = Mixer(commit=False)

    def test_is_safe_by_default(self):
        """
        By default all should be safe
        """
        self.assertTrue(self.src._ExternalEventSource__is_safe())

    def test_is_safe_with_10_events(self):
        """
        Try to replace 10 events by 8 events
        """
        for i in range(0, 10):
            mixer.blend(ExternalEvent, teacher=self.teacher, src=self.src)

        for i in range(0, 8):  # create 8 non-saved events
            self.src.events.append(
                self.safe_mixer.blend(ExternalEvent, teacher=self.teacher, src=self.src)
            )

        self.assertTrue(self.src._ExternalEventSource__is_safe())

    def test_is_safe_to_delete_10_recurring_event(self):
        """
        Try to replace 12 events (10 of them recurring) with 2 events
        """
        mixer.blend(ExternalEvent, teacher=self.teacher, src=self.src)  # some event
        parent_event = mixer.blend(ExternalEvent, teacher=self.teacher, src=self.src)  # this event will be parent to 10 others

        for i in range(0, 10):
            mixer.blend(ExternalEvent, teacher=self.teacher, src=self.src, parent=parent_event)

        for i in range(0, 2):  # create 2 non-saved events
            self.src.events.append(
                self.safe_mixer.blend(ExternalEvent, teacher=self.teacher, src=self.src)
            )

        self.assertTrue(self.src._ExternalEventSource__is_safe())

    def test_unsafe_with_zero_events(self):
        """
        Try to replace 10 events by 0 events
        """
        for i in range(0, 10):
            mixer.blend(ExternalEvent, teacher=self.teacher, src=self.src)

        self.assertFalse(self.src._ExternalEventSource__is_safe())

    def test_unsafe_with_more_then_two_times_difference(self):
        """
        Try to replace 10 events by 3 events
        """
        for i in range(0, 10):
            mixer.blend(ExternalEvent, teacher=self.teacher, src=self.src)

        for i in range(0, 3):  # create 3 non-saved events
            self.src.events.append(
                self.safe_mixer.blend(ExternalEvent, teacher=self.teacher, src=self.src)
            )

        self.assertFalse(self.src._ExternalEventSource__is_safe())

