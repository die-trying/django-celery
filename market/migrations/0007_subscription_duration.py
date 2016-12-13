# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0006_auto_20161117_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='duration',
            field=models.DurationField(editable=False, default=timedelta(days=7 * 6)),
            preserve_default=False,
        ),
    ]
