# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import django_markdown.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20160629_1301'),
    ]

    operations = [
        migrations.CreateModel(
            name='HappyHour',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
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
            name='PairedLesson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
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
        migrations.AddField(
            model_name='lessonwithnative',
            name='slots',
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='ordinarylesson',
            name='slots',
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='product1',
            name='happy_hours',
            field=models.ManyToManyField(to='products.HappyHour'),
        ),
        migrations.AddField(
            model_name='product1',
            name='master_classes',
            field=models.ManyToManyField(to='products.MasterClass'),
        ),
        migrations.AddField(
            model_name='product1',
            name='paired_lessons',
            field=models.ManyToManyField(to='products.PairedLesson'),
        ),
    ]
