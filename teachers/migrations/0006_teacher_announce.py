# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_markdown.models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0005_teacher_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='announce',
            field=django_markdown.models.MarkdownField(verbose_name='Short description', default=''),
            preserve_default=False,
        ),
    ]
