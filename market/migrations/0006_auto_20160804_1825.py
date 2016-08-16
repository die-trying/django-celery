# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0005_auto_20160802_1458'),
    ]

    operations = [
        migrations.RenameField(
            model_name='class',
            old_name='timeline_entry',
            new_name='timeline',
        ),
    ]
