from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer, create_teacher


class TestClass(TestCase):
    def setUp(self):
        self.teacher = create_teacher()
        self.customer = create_customer()

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
