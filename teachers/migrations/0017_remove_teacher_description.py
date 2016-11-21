# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0016_teacher_teacher_avatar_cropping'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='description',
        ),
    ]
