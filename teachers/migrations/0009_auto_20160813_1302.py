# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('teachers', '0008_auto_20160809_1816'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teacher',
            old_name='acceptable_lessons',
            new_name='allowed_lessons',
        ),
    ]
