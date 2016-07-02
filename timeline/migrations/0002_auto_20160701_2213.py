# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='event_type',
            field=models.ForeignKey(blank=True, null=True, to='contenttypes.ContentType', default=3),
        ),
    ]
