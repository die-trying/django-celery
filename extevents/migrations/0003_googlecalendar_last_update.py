# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('extevents', '0002_auto_20160912_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='googlecalendar',
            name='last_update',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 9, 13, 18, 38, 49, 622910, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
