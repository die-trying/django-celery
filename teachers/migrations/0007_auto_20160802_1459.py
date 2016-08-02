# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0006_teacher_announce'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='acceptable_lessons',
            field=models.ManyToManyField(to='contenttypes.ContentType', blank=True, related_name='_teacher_acceptable_lessons_+'),
        ),
    ]
