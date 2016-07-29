# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import django_markdown.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('lessons', '0001_initial'), ('lessons', '0002_event')]

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HappyHour',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=140)),
                ('internal_name', models.CharField(max_length=140)),
                ('duration', models.DurationField(default=datetime.timedelta(0, 1800))),
                ('description', django_markdown.models.MarkdownField()),
                ('slots', models.SmallIntegerField(default=1)),
                ('active', models.IntegerField(default=1, choices=[(0, 'Inactive'), (1, 'Active')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LessonWithNative',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=140)),
                ('internal_name', models.CharField(max_length=140)),
                ('duration', models.DurationField(default=datetime.timedelta(0, 1800))),
                ('description', django_markdown.models.MarkdownField()),
                ('slots', models.SmallIntegerField(default=1)),
                ('active', models.IntegerField(default=1, choices=[(0, 'Inactive'), (1, 'Active')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MasterClass',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=140)),
                ('internal_name', models.CharField(max_length=140)),
                ('duration', models.DurationField(default=datetime.timedelta(0, 1800))),
                ('description', django_markdown.models.MarkdownField()),
                ('slots', models.SmallIntegerField(default=1)),
                ('active', models.IntegerField(default=1, choices=[(0, 'Inactive'), (1, 'Active')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrdinaryLesson',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=140)),
                ('internal_name', models.CharField(max_length=140)),
                ('duration', models.DurationField(default=datetime.timedelta(0, 1800))),
                ('description', django_markdown.models.MarkdownField()),
                ('slots', models.SmallIntegerField(default=1)),
                ('active', models.IntegerField(default=1, choices=[(0, 'Inactive'), (1, 'Active')])),
            ],
            options={
                'verbose_name': 'Usual curated lesson',
            },
        ),
        migrations.CreateModel(
            name='PairedLesson',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=140)),
                ('internal_name', models.CharField(max_length=140)),
                ('duration', models.DurationField(default=datetime.timedelta(0, 1800))),
                ('description', django_markdown.models.MarkdownField()),
                ('slots', models.SmallIntegerField(default=1)),
                ('active', models.IntegerField(default=1, choices=[(0, 'Inactive'), (1, 'Active')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=140)),
                ('internal_name', models.CharField(max_length=140)),
                ('description', django_markdown.models.MarkdownField()),
                ('duration', models.DurationField(default=datetime.timedelta(0, 1800))),
                ('host', models.ForeignKey(related_name='hosted_events', to=settings.AUTH_USER_MODEL)),
                ('lesson_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
    ]
