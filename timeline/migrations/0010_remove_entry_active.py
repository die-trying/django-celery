# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0009_auto_20161023_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='active',
        ),
    ]
