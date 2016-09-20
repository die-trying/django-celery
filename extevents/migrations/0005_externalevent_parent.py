# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extevents', '0004_auto_20160918_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='externalevent',
            name='parent',
            field=models.ForeignKey(to='extevents.ExternalEvent', null=True, blank=True),
        ),
    ]
