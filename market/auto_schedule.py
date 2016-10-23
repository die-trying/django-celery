from collections import UserList
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from teachers.slot_list import SlotList


class BusyPeriods(UserList):
    """
    Abstract representation of a busy period
    """
    def __init__(self, queryset, start_field='start', end_field='end'):
        super().__init__()
        for absense in queryset.values(start_field, end_field):
            self.data.append(absense)

    def is_present(self, start, end):
        """
        Return True if the event is not found in the abscence list
        """
        for period in self.data:
            if start >= period['start'] and start < period['end']:
                return False
            if end > period['start'] and end <= period['end']:
                return False

        return True


class AutoSchedule():
    """
    Big class for automatically generating teachers schedule
    """
    def __init__(self, teacher):
        super().__init__()

        self.teacher = teacher

        self.extevents = BusyPeriods(teacher.busy_periods.all())
        self.absenses = BusyPeriods(teacher.absences.approved())
        self.timeline_entries = BusyPeriods(teacher.timeline_entries.filter(end__gte=timezone.now()))

    def slots(self, start, end, period=timedelta(minutes=30)):
        """
        Return a slot list with available time slots
        """
        slot_list = SlotList()
        while start <= end - period:
            try:
                self.clean(start, start + period)
            except ValidationError:
                continue
            else:
                slot_list.append(start)
            finally:
                start += period

        return slot_list

    def clean(self, start, end):
        if start < timezone.now() or end < timezone.now():
            raise ValidationError('Entry is in past!')

        if not self.absenses.is_present(start, end):
            raise ValidationError('Teacher has a registered absence')

        if not self.extevents.is_present(start, end):
            raise ValidationError('Teacher has a personal event in this period')

        if not self.timeline_entries.is_present(start, end):
            raise ValidationError('Teacher has other lessons in this period')
