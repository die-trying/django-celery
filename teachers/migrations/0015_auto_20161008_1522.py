# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import image_cropping.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0014_auto_20160925_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='teacher_photo',
            field=models.ImageField(blank=True, upload_to='teachers/', null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='teacher_photo_cropping',
            field=image_cropping.fields.ImageRatioField('teacher_photo', '500x500', adapt_rotation=False, verbose_name='teacher photo cropping', hide_image_field=False, size_warning=False, free_crop=False, help_text=None, allow_fullsize=False),
        ),
    ]
