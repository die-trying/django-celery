# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import image_cropping.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0015_auto_20161008_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='teacher_avatar_cropping',
            field=image_cropping.fields.ImageRatioField('teacher_photo', '80x80', size_warning=False, hide_image_field=False, verbose_name='teacher avatar cropping', allow_fullsize=False, help_text=None, free_crop=False, adapt_rotation=False),
        ),
    ]
