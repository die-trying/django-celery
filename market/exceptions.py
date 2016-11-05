from django.core.exceptions import ValidationError


class CannotBeScheduled(Exception):
    """
    Indicates a situation when trying to schedule lesson that does not suite
    to a timeline entry
    """
    pass


class AutoScheduleExpcetion(ValidationError):
    """
    Indicates error in AutoSchedule, when teacher is not available
    """
    pass
