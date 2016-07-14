# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0007_auto_20160714_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='active',
            field=models.SmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active')], default=1),
        ),
    ]
