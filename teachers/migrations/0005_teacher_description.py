# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_markdown.models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0004_teacher_acceptable_lessons'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='description',
            field=django_markdown.models.MarkdownField(default=''),
            preserve_default=False,
        ),
    ]
