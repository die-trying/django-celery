# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('teachers', '0003_auto_20160718_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='acceptable_lessons',
            field=models.ManyToManyField(related_name='+', to='contenttypes.ContentType'),
        ),
    ]
