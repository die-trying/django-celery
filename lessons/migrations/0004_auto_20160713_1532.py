# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lessons', '0003_event_slots'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='host',
        ),
        migrations.RemoveField(
            model_name='event',
            name='lesson_type',
        ),
        migrations.AddField(
            model_name='happyhour',
            name='host',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='+'),
        ),
        migrations.AddField(
            model_name='masterclass',
            name='host',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='+'),
        ),
        migrations.DeleteModel(
            name='Event',
        ),
    ]
