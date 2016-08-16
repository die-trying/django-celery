# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0004_class_buy_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='class',
            options={'get_latest_by': 'buy_date'},
        ),
        migrations.AlterField(
            model_name='class',
            name='subscription',
            field=models.ForeignKey(null=True, related_name='classes', blank=True, to='market.Subscription'),
        ),
        migrations.AlterField(
            model_name='class',
            name='timeline_entry',
            field=models.ForeignKey(null=True, related_name='classes', blank=True, on_delete=django.db.models.deletion.SET_NULL, to='timeline.Entry'),
        ),
    ]
