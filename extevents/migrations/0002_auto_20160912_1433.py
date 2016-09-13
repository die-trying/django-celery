# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('teachers', '0012_auto_20160910_1235'),
        ('extevents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalEvent',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('ext_src_id', models.PositiveIntegerField()),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('description', models.CharField(max_length=140)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('ext_src_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('teacher', models.ForeignKey(to='teachers.Teacher', related_name='busy_periods')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='externalevent',
            unique_together=set([('teacher', 'ext_src_type', 'ext_src_id', 'start', 'end')]),
        ),
    ]
