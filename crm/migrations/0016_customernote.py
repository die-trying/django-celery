# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0010_teacher_active'),
        ('crm', '0015_customer_languages'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('customer', models.ForeignKey(to='crm.Customer', related_name='notes')),
                ('teacher', models.ForeignKey(to='teachers.Teacher', related_name='customer_notes')),
            ],
            options={
                'verbose_name': 'Note',
                'verbose_name_plural': 'Customer notes',
            },
        ),
    ]
