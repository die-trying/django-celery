# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0003_auto_20160719_0702'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='allow_besides_working_hours',
            field=models.BooleanField(default=True),
        ),
    ]
