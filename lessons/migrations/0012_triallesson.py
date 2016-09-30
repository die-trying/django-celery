# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import django_markdown.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0011_auto_20160926_1543'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrialLesson',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=140)),
                ('internal_name', models.CharField(max_length=140)),
                ('duration', models.DurationField(default=datetime.timedelta(0, 1800))),
                ('announce', django_markdown.models.MarkdownField()),
                ('description', django_markdown.models.MarkdownField()),
                ('slots', models.SmallIntegerField(default=1)),
                ('active', models.IntegerField(default=1, choices=[(0, 'Inactive'), (1, 'Active')])),
            ],
            options={
                'verbose_name': 'First lesson',
                'abstract': False,
            },
        ),
    ]
