# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [('timeline', '0001_initial'), ('timeline', '0002_auto_20160630_1239'), ('timeline', '0003_auto_20160701_0401')]

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('start_time', models.DateTimeField()),
                ('duration', models.DurationField(default=datetime.timedelta(0, 1800))),
                ('slots', models.SmallIntegerField()),
                ('customer', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='planned_lessons', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('teacher', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='timeline_entries', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
        ),
        migrations.AlterModelOptions(
            name='entry',
            options={'verbose_name_plural': 'Entries'},
        ),
        migrations.AddField(
            model_name='entry',
            name='event_id',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='entry',
            name='event_type',
            field=models.ForeignKey(null=True, to='contenttypes.ContentType', blank=True),
        ),
    ]
