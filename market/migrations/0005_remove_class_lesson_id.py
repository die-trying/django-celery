# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0004_auto_20161005_1552'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='class',
            name='lesson_id',
        ),
    ]
