# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hub', '0002_class_event'),
    ]

    operations = [
        migrations.RenameField(
            model_name='class',
            old_name='event',
            new_name='timeline_entry',
        ),
    ]
