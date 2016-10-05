from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer, create_teacher
from manual_class_logging.models import ManualClassLogEntry
from market.models import Class
from timeline.models import Entry as TimelineEntry


class TestClass(TestCase):
    fixtures = ('crm', 'lessons')

    def setUp(self):
        self.teacher = create_teacher()
        self.customer = create_customer()

    def test_finish_date_none(self):
        c = mixer.blend(Class, customer=self.customer, is_fully_used=False)

        self.assertIsNone(c.finish_time)

    def test_finish_time_timeline_entry(self):
        c = mixer.blend(Class, customer=self.customer, is_fully_used=True)
        entry = mixer.blend(TimelineEntry, teacher=self.teacher, start=self.tzdatetime(2016, 12, 11, 15, 0))
        c.timeline = entry
        self.assertEqual(c.finish_time, self.tzdatetime(2016, 12, 11, 15, 0))

    def test_finish_time_manual_completion_log_entry(self):
        c = mixer.blend(Class, customer=self.customer, is_fully_used=True)
        log_entry = mixer.blend(
            ManualClassLogEntry,
            teacher=self.teacher,
            Class=c,
        )
        log_entry.timestamp = self.tzdatetime(2016, 12, 11, 15, 0)
        log_entry.save()

        c.refresh_from_db()
        self.assertEqual(c.finish_time, self.tzdatetime(2016, 12, 11, 15, 0))
