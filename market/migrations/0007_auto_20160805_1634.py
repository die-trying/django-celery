# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0006_auto_20160804_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='pre_start_notifications_sent_to_student',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='class',
            name='pre_start_notifications_sent_to_teacher',
            field=models.BooleanField(default=False),
        ),
    ]
