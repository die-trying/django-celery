"""
    Shortcuts for dealing with timedelta in format, unsderstandable by django
    models.
"""
from copy import copy
from datetime import date, datetime, time, timedelta

import pytz
from django.utils.dateformat import format


def minute_till_midnight(date):
    return datetime.combine(date, time.max)


def minute_after_midnight(date):
    return datetime.combine(date + timedelta(days=1), time.min)


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


def day_range(d):
    """
    Return a day range for model query — a tuple with start of the day and end of the day
    """
    if isinstance(d, date):
        d = d.strftime('%Y-%m-%d')

    return (
        d + ' 00:00:00',
        d + ' 23:59:59',
    )


def common_timezones():
    """
    List of common timezones

    Excludes some rare and unneeded to the app timezones, like Asia or Antarctica ones
    """
    for tz in pytz.common_timezones:
        if tz.startswith('Europe/') or tz.startswith('US/'):
            yield (tz, tz)

    yield ('UTC', 'UTC')
