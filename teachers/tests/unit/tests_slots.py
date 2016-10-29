
from django.test import override_settings
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_teacher
from teachers.api.serializers import TimeSlotSerializer
from teachers.models import SlotList, WorkingHours


@override_settings(UZE_TZ=True, TIME_ZONE='UTC')
class TestSlotsIterable(TestCase):
    def _generate_slots(self):
        teacher = create_teacher()
        mixer.blend(WorkingHours, teacher=teacher, weekday=0, start='13:00', end='15:00')
        return teacher.find_free_slots(date=self.tzdatetime(2032, 5, 3))

    def test_count(self):
        slots = TimeSlotSerializer(self._generate_slots(), many=True).data

        self.assertEquals(len(slots), 4)
        self.assertEquals(slots[0]['server'], '13:00')
        self.assertEquals(slots[-1]['server'], '14:30')

    def test_sort(self):
        def dt(*args):
            return self.tzdatetime(*args)

        slots = SlotList()
        for i in (dt(2016, 1, 1, 13, 0), dt(2016, 1, 1, 11, 0), dt(2016, 1, 1, 11, 1), dt(2016, 1, 1, 14, 0)):
            slots.add(i)

        slot_list = [i['server'] for i in TimeSlotSerializer(slots, many=True).data]
        self.assertEquals(slot_list, ['11:00', '11:01', '13:00', '14:00'])
