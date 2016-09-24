# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extevents', '0005_externalevent_parent'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='externalevent',
            unique_together=set([]),
        ),
    ]
