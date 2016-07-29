# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django_markdown.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0006_auto_20160722_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='happyhour',
            name='announce',
            field=django_markdown.models.MarkdownField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lessonwithnative',
            name='announce',
            field=django_markdown.models.MarkdownField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='masterclass',
            name='announce',
            field=django_markdown.models.MarkdownField(default=' '),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ordinarylesson',
            name='announce',
            field=django_markdown.models.MarkdownField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pairedlesson',
            name='announce',
            field=django_markdown.models.MarkdownField(default=''),
            preserve_default=False,
        ),
    ]
