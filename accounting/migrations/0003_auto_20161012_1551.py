# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0002_auto_20160925_0847'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([]),
        ),
    ]
