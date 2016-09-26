# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0010_teacher_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Absence',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('type', models.CharField(choices=[('vacation', 'Vacation'), ('unpaid', 'Unpaid'), ('sick', 'Sick leave'), ('bonus', 'Bonus vacation'), ('srv', 'System-intiated vacation')], max_length=32, default='srv')),
                ('start', models.DateTimeField(verbose_name='Start')),
                ('end', models.DateTimeField(verbose_name='End')),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=True)),
                ('teacher', models.ForeignKey(to='teachers.Teacher', related_name='absences')),
            ],
        ),
    ]
