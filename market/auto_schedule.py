from collections import UserList
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from market.exceptions import AutoScheduleExpcetion
from teachers.slot_list import SlotList


class TeacherHasEvents(AutoScheduleExpcetion):
    pass


class TeacherIsAbsent(AutoScheduleExpcetion):
    pass


class TeacherHasOtherLessons(AutoScheduleExpcetion):
    pass


class EntryIsInPast(AutoScheduleExpcetion):
    pass


class BusyPeriods(UserList):
    """
    Abstract representation of a busy period

    Params:
        - queryset: a querset with periods of inavailability
        - start_field: field with a period start (default: 'start')
        - end_field: field with a period end (default: 'end')
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
    def __init__(self, teacher, exclude_timeline_entries=[]):
        super().__init__()

        self.teacher = teacher

        if None in exclude_timeline_entries:
            exclude_timeline_entries.remove(None)  # There is a difference between exclude(pk__in=[]) and exclude(pk__in=[None]). The latter breaks the whole query.

        self.busy_periods = {
            'extevents': {
                'src': BusyPeriods(teacher.busy_periods.all()),
                'exception': TeacherHasEvents,
            },
            'absences': {
                'src': BusyPeriods(teacher.absences.approved()),
                'exception': TeacherIsAbsent,
            },
            'other_entries': {
                'src': BusyPeriods(teacher.timeline_entries.filter(end__gte=timezone.now()).exclude(pk__in=exclude_timeline_entries)),
                'exception': TeacherHasOtherLessons,
            },
        }

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
                slot_list.add(start)
            finally:
                start += period

        return slot_list

    def test(self, period_type, start, end):
        busy_period = self.busy_periods.get(period_type)

        return busy_period['src'].is_present(start, end)

    def clean(self, start, end):
        if start < timezone.now() or end < timezone.now():
            raise EntryIsInPast('Entry is in past!')

        print(self.busy_periods)
        for period_type, busy_period in self.busy_periods.items():
            if not self.test(period_type, start, end):
                raise busy_period['exception']('Autoschedule validation error: %s' % period_type)
