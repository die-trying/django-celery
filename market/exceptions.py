class CannotBeScheduled(Exception):
    """
    Indicates a situation when trying to schedule lesson that does not suite
    to a timeline entry
    """
    pass


class CannotBeUnscheduled(Exception):
    """
    Indicates a situation when we can not un-schedule a lesson
    """
    pass
