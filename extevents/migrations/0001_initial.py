# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0012_auto_20160910_1235'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoogleCalendar',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('url', models.URLField()),
                ('active', models.BooleanField(default=True)),
                ('teacher', models.ForeignKey(related_name='google_calendars', to='teachers.Teacher')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
