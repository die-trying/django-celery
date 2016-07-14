"""
    Shortcuts for dealing with timedelta in format, unsderstandable by django
    models.
"""
from copy import copy
from datetime import datetime, timedelta

from django.utils.dateformat import format


def ago(date=datetime.now(), fmt='Y-m-d', **kwargs):
    """
    Move date backwards. Arguments are compatible with `timedelta<https://docs.python.org/3/library/datetime.html#datetime.timedelta>`_
    """
    d = copy(date)
    d -= timedelta(**kwargs)
    return format(d, fmt)


def fwd(date=datetime.now(), fmt='Y-m-d', **kwargs):
    """
    Move date forward. Arguments are compatible with `timedelta<https://docs.python.org/3/library/datetime.html#datetime.timedelta>`_
    """
    d = copy(date)
    d += timedelta(**kwargs)
    return format(d, fmt)
