# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0001_squashed_0002_event'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='happyhour',
            options={'verbose_name': 'Happy Hour'},
        ),
        migrations.AlterModelOptions(
            name='lessonwithnative',
            options={'verbose_name_plural': 'Curated lessons with native speaker', 'verbose_name': 'Curataed lesson with native speaker'},
        ),
        migrations.AlterModelOptions(
            name='masterclass',
            options={'verbose_name_plural': 'Master Classes', 'verbose_name': 'Master Class'},
        ),
        migrations.AlterModelOptions(
            name='pairedlesson',
            options={'verbose_name': 'Paired Lesson'},
        ),
    ]
