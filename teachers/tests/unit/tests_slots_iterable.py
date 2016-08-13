from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from mixer.backend.django import mixer

from elk.utils.testing import create_teacher
from teachers.models import SlotList, WorkingHours


class TestSlotsIterable(TestCase):
    def _generate_slots(self):
        teacher = create_teacher()
        mixer.blend(WorkingHours, teacher=teacher, weekday=0, start='13:00', end='15:00')
        return teacher.find_free_slots(date='2032-05-03')

    def test_as_dict(self):
        slots = self._generate_slots()
        slot_list = slots.as_dict()
        self.assertEquals(len(slot_list), 4)
        self.assertEquals(slot_list[0], '13:00')
        self.assertEquals(slot_list[-1], '14:30')

    def test_sort(self):
        def dt(*args):
            return timezone.make_aware(datetime(*args))

        slots = SlotList()
        for i in (dt(2016, 1, 1, 13, 0), dt(2016, 1, 1, 11, 0), dt(2016, 1, 1, 11, 1), dt(2016, 1, 1, 14, 0)):
            slots.append(i)
        slot_list = slots.as_dict()
        self.assertEquals(slot_list, ['11:00', '11:01', '13:00', '14:00'])
