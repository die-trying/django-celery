# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0002_auto_20160701_0524'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='duration',
        ),
    ]
