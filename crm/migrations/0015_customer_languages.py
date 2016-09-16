# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0009_language'),
        ('crm', '0014_auto_20160916_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='languages',
            field=models.ManyToManyField(to='lessons.Language'),
        ),
    ]
