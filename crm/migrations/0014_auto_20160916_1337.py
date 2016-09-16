# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0013_auto_20160909_0601'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='responsible',
            new_name='curator',
        ),
    ]
