# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0003_class_is_scheduled'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='buy_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 7, 24, 8, 30, 34, 892984)),
            preserve_default=False,
        ),
    ]
