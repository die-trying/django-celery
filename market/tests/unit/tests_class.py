from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer, create_teacher


class TestClass(TestCase):
    def setUp(self):
        self.teacher = create_teacher()
        self.customer = create_customer()

    def test_finish_date_none(self):
        c = mixer.blend('market.Class', customer=self.customer, is_fully_used=False)

        self.assertIsNone(c.finish_time)

    def test_finish_time_timeline_entry(self):
        c = mixer.blend('market.Class', customer=self.customer, is_fully_used=True)
        entry = mixer.blend('timeline.Entry', teacher=self.teacher, start=self.tzdatetime(2016, 12, 11, 15, 0))
        c.timeline = entry
        self.assertEqual(c.finish_time, self.tzdatetime(2016, 12, 11, 15, 0))

    def test_finish_time_manual_completion_log_entry(self):
        c = mixer.blend('market.Class', customer=self.customer, is_fully_used=True)
        log_entry = mixer.blend(
            'manual_class_logging.ManualClassLogEntry',
            teacher=self.teacher,
            Class=c,
        )
        log_entry.timestamp = self.tzdatetime(2016, 12, 11, 15, 0)
        log_entry.save()

        c.refresh_from_db()
        self.assertEqual(c.finish_time, self.tzdatetime(2016, 12, 11, 15, 0))

    def test_has_started_without_entry(self):
        c = mixer.blend('market.Class', customer=self.customer, is_fully_used=True)

        self.assertFalse(c.has_started())

    def test_has_started_true(self):
        c = mixer.blend('market.Class', customer=self.customer)
        entry = mixer.blend('timeline.Entry', teacher=self.teacher, start=self.tzdatetime(2016, 12, 11, 15, 0))
        c.timeline = entry

        with freeze_time('2016-12-11 20:00'):  # move to the future
            self.assertTrue(c.has_started())

    def test_has_started_false(self):
        c = mixer.blend('market.Class', customer=self.customer)
        entry = mixer.blend('timeline.Entry', teacher=self.teacher, start=self.tzdatetime(2016, 12, 11, 15, 0))
        c.timeline = entry

        with freeze_time('2016-12-11 10:00'):  # move to the past
            self.assertFalse(c.has_started())
