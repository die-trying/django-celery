# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0001_squashed_0003_auto_20160701_0401'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='slots',
        ),
        migrations.AlterField(
            model_name='entry',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='planned_lessons', null=True, blank=True, to='crm.Customer'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='timeline_entries', to=settings.AUTH_USER_MODEL),
        ),
    ]
