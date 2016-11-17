# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0005_remove_class_lesson_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='class',
            name='active',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='active',
        ),
    ]
