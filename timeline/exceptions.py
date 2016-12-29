from django.core.exceptions import ValidationError  # noqa

from market.exceptions import AutoScheduleExpcetion  # noqa


class DoesNotFitWorkingHours(ValidationError):
    pass
