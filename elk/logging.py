import logging

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType


def _get_logger():
    return logging.getLogger('app')


class logger():
    @staticmethod
    def warning(*args, **kwargs):
        kwargs['exc_info'] = True
        _get_logger().warning(*args, **kwargs)

    @staticmethod
    def error(*args, **kwargs):
        kwargs['exc_info'] = True
        _get_logger().error(*args, **kwargs)


def write_admin_log_entry(user, object, action_flag=None, msg='Changed'):
    """
    Create a django bundled admin log entry
    """
    if action_flag is None:
        action_flag = admin.models.CHANGE

    entry = admin.models.LogEntry(
        user=user,
        object_id=object.pk,
        content_type=ContentType.objects.get_for_model(object),  # move it away from this function if you experience problems
        object_repr=str(object),
        action_flag=action_flag,
        change_message=msg,
    )
    entry.save()
