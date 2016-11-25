# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0017_remove_teacher_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='title',
            field=models.TextField(max_length=32, blank=True),
        ),
    ]
