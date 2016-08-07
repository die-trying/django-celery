# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_auto_20160714_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='cancellation_streak',
            field=models.SmallIntegerField(verbose_name='Cancelled lesson streak', default=0),
        ),
        migrations.AddField(
            model_name='customer',
            name='max_cancellation_count',
            field=models.SmallIntegerField(verbose_name='Maximum allowed lessons to cancel', default=2),
        ),
    ]
