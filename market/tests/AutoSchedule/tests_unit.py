from datetime import timedelta

from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_teacher
from market.auto_schedule import AutoSchedule, BusyPeriods


class TestBusyPeriods(TestCase):
    def setUp(self):
        self.teacher = create_teacher()
        mixer.blend(
            'extevents.ExternalEvent',
            teacher=self.teacher,
            start=self.tzdatetime(2032, 12, 5, 13, 30),
            end=self.tzdatetime(2032, 12, 5, 14, 30),
        )

    def test_from_queryset(self):
        for i in range(0, 10):
            mixer.blend('extevents.ExternalEvent', teacher=self.teacher)

        absenses = BusyPeriods(self.teacher.busy_periods)
        self.assertEqual(len(absenses), 11)

    def test_within_period(self):
        absenses = BusyPeriods(self.teacher.busy_periods)

        self.assertFalse(absenses.is_present(
            start=self.tzdatetime(2032, 12, 5, 13, 40),
            end=self.tzdatetime(2032, 12, 5, 13, 45),
        ))

    def test_outside_period(self):
        absenses = BusyPeriods(self.teacher.busy_periods)

        self.assertTrue(absenses.is_present(
            start=self.tzdatetime(2032, 12, 5, 15, 40),
            end=self.tzdatetime(2032, 12, 5, 19, 45),
        ))

    def test_ends_outside_period(self):
        absenses = BusyPeriods(self.teacher.busy_periods)

        self.assertFalse(absenses.is_present(
            start=self.tzdatetime(2032, 12, 5, 13, 40),
            end=self.tzdatetime(2032, 12, 5, 15, 30),
        ))

    def test_start_outside_period(self):
        absenses = BusyPeriods(self.teacher.busy_periods)

        self.assertFalse(absenses.is_present(
            start=self.tzdatetime(2032, 12, 5, 13, 00),
            end=self.tzdatetime(2032, 12, 5, 14, 00),
        ))

    def test_starts_right_at_the_beginning_of_the_period(self):
        absenses = BusyPeriods(self.teacher.busy_periods)

        self.assertFalse(absenses.is_present(
            start=self.tzdatetime(2032, 12, 5, 13, 30),
            end=self.tzdatetime(2032, 12, 5, 13, 45),
        ))

    def test_ends_right_at_the_end_of_the_period(self):
        absenses = BusyPeriods(self.teacher.busy_periods)

        self.assertFalse(absenses.is_present(
            start=self.tzdatetime(2032, 12, 5, 14, 45),
            end=self.tzdatetime(2032, 12, 5, 14, 30),
        ))

    def test_starts_right_at_the_end_of_period(self):
        absenses = BusyPeriods(self.teacher.busy_periods)

        self.assertTrue(absenses.is_present(
            start=self.tzdatetime(2032, 12, 5, 14, 30),
            end=self.tzdatetime(2032, 12, 5, 14, 45),
        ))

    def test_ends_right_at_the_end_of_period(self):
        absenses = BusyPeriods(self.teacher.busy_periods)

        self.assertTrue(absenses.is_present(
            start=self.tzdatetime(2032, 12, 5, 13, 00),
            end=self.tzdatetime(2032, 12, 5, 13, 30),
        ))


class TestAutoschedule(TestCase):
    def setUp(self):
        self.teacher = create_teacher()

    def test_init_extevents(self):
        for i in range(0, 10):
            mixer.blend('extevents.ExternalEvent', teacher=self.teacher)

        s = AutoSchedule(self.teacher)
        self.assertEqual(len(s.extevents), 10)

    def test_init_absenses(self):
        for i in range(0, 10):
            mixer.blend('teachers.Absence', teacher=self.teacher, approved=True)

        s = AutoSchedule(self.teacher)
        self.assertEqual(len(s.absenses), 10)

    @freeze_time('2032-12-05 13:30')
    def test_init_timeline_entries(self):
        start = self.tzdatetime(2032, 12, 5, 14, 0)
        for i in range(0, 10):
            end = start + timedelta(minutes=30)
            mixer.blend('timeline.Entry', teacher=self.teacher, start=start, end=end)
            start = end

        s = AutoSchedule(self.teacher)
        self.assertEqual(len(s.timeline_entries), 10)

    def test_slots(self):
        s = AutoSchedule(self.teacher)

        start = self.tzdatetime(2032, 12, 5, 14, 0)
        slot_list = s.slots(start, start + timedelta(hours=2))

        self.assertEqual(len(slot_list), 4)

    def test_bypass_absenses(self):
        mixer.blend(
            'teachers.Absence',
            teacher=self.teacher,
            start=self.tzdatetime(2032, 12, 5, 14, 30),
            end=self.tzdatetime(2032, 12, 5, 14, 45),
        )
        s = AutoSchedule(self.teacher)

        start = self.tzdatetime(2032, 12, 5, 14, 0)
        slot_list = s.slots(start, start + timedelta(hours=2))
        self.assertEqual(len(slot_list), 3)

    def test_bypass_extevents(self):
        mixer.blend(
            'extevents.ExternalEvent',
            teacher=self.teacher,
            start=self.tzdatetime(2032, 12, 5, 14, 30),
            end=self.tzdatetime(2032, 12, 5, 14, 45),
        )
        s = AutoSchedule(self.teacher)

        start = self.tzdatetime(2032, 12, 5, 14, 0)
        slot_list = s.slots(start, start + timedelta(hours=2))
        self.assertEqual(len(slot_list), 3)

    @freeze_time('2032-12-05 13:30')
    def test_bypass_other_timeline_entries(self):
        start = self.tzdatetime(2032, 12, 5, 14, 0)
        mixer.blend('timeline.Entry', teacher=self.teacher, start=start, end=start + timedelta(minutes=30))

        s = AutoSchedule(self.teacher)
        slot_list = s.slots(start, start + timedelta(hours=2))
        self.assertEqual(len(slot_list), 3)
