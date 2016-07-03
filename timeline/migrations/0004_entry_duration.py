# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0003_auto_20160702_0735'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='duration',
            field=models.DurationField(default=datetime.timedelta(0, 1800)),
        ),
    ]
