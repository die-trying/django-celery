# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def mark_double_scheduled_classes(apps, schema_editor):
    """
    This migration fixes classes, that are double-scheduled: they were marked as used
    by hand, and then they were still able to be scheduled.

    For details of the fix, see the rest of the commit
    """
    Class = apps.get_model('market.Class')
    for c in Class.objects.filter(timeline__isnull=False):
        print("Got double-marked class for", c.customer.user.first_name, c.customer.user.last_name)
        print(" → Double marked class id", c.pk)
        print(" → Findind the actual class to mark as used")
        actual_class = Class.objects.filter(customer=c.customer) \
            .filter(is_fully_used=False) \
            .filter(is_scheduled=False) \
            .filter(lesson_type=c.lesson_type) \
            .order_by('subscription_id', 'buy_date') \
            .first()
        if actual_class is not None:
            print(" → Found the actual class", actual_class.pk)
        else:
            print(" → Actual class is not found, trying to finish class of any lesson_type...")
            actual_class = Class.objects.filter(customer=c.customer) \
                .filter(is_fully_used=False) \
                .filter(is_scheduled=False) \
                .order_by('subscription_id', 'buy_date') \
                .first()
            assert actual_class is not None, "No classes found, bailing out"
            print(" → Found the actual class with other lesson_type", actual_class.pk)

        print(" → Removing timeline entry from the double-marked class")

        timeline_entry = c.timeline
        schema_editor.execute("UPDATE market_class SET timeline_id=NULL WHERE id=%d" % c.pk)

        print(" → Attaching the actual class to the timeline and marking as used")
        actual_class.timeline = timeline_entry
        actual_class.is_fully_used = True
        actual_class.is_scheduled = True

        actual_class.save()


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0002_auto_20160818_1546'),
    ]

    operations = [
        migrations.RunPython(mark_double_scheduled_classes)
    ]
