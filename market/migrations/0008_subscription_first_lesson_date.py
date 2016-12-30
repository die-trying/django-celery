# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def add_first_lesson_date(apps, schema_editor):
    """
    Set first lesson date for all subscriptions that have passed classes
    """
    Subscription = apps.get_model('market.subscription')

    for s in Subscription.objects.filter(first_lesson_date__isnull=True):
        first_class = s.classes.filter(subscription=s, timeline__isnull=False).order_by('timeline__start').first()

        if first_class is not None:
            s.first_lesson_date = first_class.timeline.start
            s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0007_subscription_duration'),
        ('timeline', '0012_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='first_lesson_date',
            field=models.DateTimeField(null=True, editable=False, verbose_name='Date of the first lesson')
        ),
        migrations.RunPython(add_first_lesson_date),
    ]
