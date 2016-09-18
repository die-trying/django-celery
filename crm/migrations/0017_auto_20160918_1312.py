# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0016_customernote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='languages',
            field=models.ManyToManyField(to='lessons.Language', blank=True),
        ),
    ]
