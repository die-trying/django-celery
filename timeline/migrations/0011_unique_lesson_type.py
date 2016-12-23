# -*- coding: utf-8 -*-
#
# This migrations adds a constraint, that teacher can schedule only one lesson_type at a time
# Without this contstraint the SortingHat can produce weird results, because teachers can create
# two lessons of a single class (e.g. two Master Classes) at a single time.
#
from __future__ import unicode_literals

from django.db import migrations

DUPLICATED_TIMELINE_ENTRIES = [129, 131]


def cancel_duplicated_timeline_entries(apps, schema_editor):
    """
    Clean already garbled timeline table from duplicated entries
    """
    TimelineEntry = apps.get_model('timeline.Entry')

    for pk in DUPLICATED_TIMELINE_ENTRIES:
        TimelineEntry.objects.get(pk=pk).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('timeline', '0010_remove_entry_active'),
    ]

    operations = [
        migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE'),
        migrations.RunPython(cancel_duplicated_timeline_entries, atomic=False),
        migrations.AlterUniqueTogether(
            name='entry',
            unique_together=set([('teacher', 'lesson_type', 'start')]),
        ),
    ]
