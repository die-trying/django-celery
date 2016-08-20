from django.dispatch import Signal, receiver

from manual_class_logging.models import ManualClassLogEntry


class_marked_as_used = Signal(providing_args=['instance', 'teacher'])
class_renewed = Signal(providing_args=['instance', 'teacher'])


@receiver(class_marked_as_used, dispatch_uid='write_manual_class_logentry')
def write_manual_class_logentry(**kwargs):
    entry = ManualClassLogEntry(
        Class=kwargs['instance'],
        teacher=kwargs['teacher'],
    )
    entry.save()


@receiver(class_renewed, dispatch_uid='remove_manual_class_logentry')
def remote_manual_class_logentry(**kwargs):
    for entry in ManualClassLogEntry.objects.filter(Class=kwargs['instance']):
        entry.delete()
