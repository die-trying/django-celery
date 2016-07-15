# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='teacher_data', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkingHours',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('weekday', models.IntegerField(verbose_name='Weekday', choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')])),
                ('start', models.TimeField(verbose_name='Start hour (UTC)')),
                ('end', models.TimeField(verbose_name='End hoour(UTC)')),
                ('teacher', models.ForeignKey(to='teachers.Teacher', related_name='working_hours')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='workinghours',
            unique_together=set([('teacher', 'weekday')]),
        ),
    ]
