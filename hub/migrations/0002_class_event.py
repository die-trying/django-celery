# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0001_initial'),
        ('hub', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='event',
            field=models.ForeignKey(null=True, related_name='classes', blank=True, to='timeline.Entry'),
        ),
    ]
