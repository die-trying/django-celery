# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='workinghours',
            options={'verbose_name_plural': 'Working hours'},
        ),
        migrations.AlterField(
            model_name='teacher',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='teacher_data', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
