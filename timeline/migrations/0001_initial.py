# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('start_time', models.DateTimeField()),
                ('duration', models.DurationField(default=datetime.timedelta(0, 1800))),
                ('slots', models.SmallIntegerField()),
                ('customer', models.ForeignKey(null=True, related_name='planned_lessons', blank=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL)),
                ('teacher', models.ForeignKey(null=True, related_name='timeline_entries', blank=True, to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL)),
            ],
        ),
    ]
