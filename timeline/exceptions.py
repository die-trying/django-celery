from django.core.exceptions import ValidationError


class DoesNotFitWorkingHours(ValidationError):
    pass
