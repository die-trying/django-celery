# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0008_entry_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entry',
            old_name='start_time',
            new_name='start',
        ),
        migrations.AddField(
            model_name='entry',
            name='end',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 16, 4, 13, 30, 608409)),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='entry',
            name='duration',
        ),
    ]
