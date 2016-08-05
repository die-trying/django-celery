from django.dispatch import Signal


class_scheduled = Signal(providing_args=['instance'])  # class is just scheduled
class_unscheduled = Signal(providing_args=['instance'])  # class is just cancelled

class_starting_teacher = Signal(providing_args=['instance'])  # class is about to start (for teachers)
class_starting_student = Signal(providing_args=['instance'])  # class is about to start (for students)
#
# i have made two different signals, because they obviously will require different
# options, like time, left to the lesson
