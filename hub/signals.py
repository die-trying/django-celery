from django.dispatch import Signal


class_scheduled = Signal(providing_args=['instance'])
class_unscheduled = Signal(providing_args=['instance'])
