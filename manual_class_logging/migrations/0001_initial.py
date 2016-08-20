# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):
    dependencies = [
        ('market', '0002_auto_20160818_1546'),
        ('teachers', '0010_teacher_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualClassLogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('Class', models.ForeignKey(to='market.Class')),
                ('teacher', models.ForeignKey(related_name='manualy_completed_classes', to='teachers.Teacher')),
                ('timestamp', models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 8, 20, 19, 5, 6, 798074, tzinfo=utc))),
            ],
        ),
    ]
