# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import image_cropping.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0012_triallesson'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='masterclass',
            options={'verbose_name': 'Round table', 'verbose_name_plural': 'Round table'},
        ),
        migrations.AddField(
            model_name='happyhour',
            name='photo',
            field=models.ImageField(blank=True, upload_to='lessons/', null=True),
        ),
        migrations.AddField(
            model_name='happyhour',
            name='photo_cropping',
            field=image_cropping.fields.ImageRatioField('photo', '500x500', verbose_name='photo cropping', help_text=None, allow_fullsize=False, adapt_rotation=False, hide_image_field=False, size_warning=False, free_crop=False),
        ),
        migrations.AddField(
            model_name='masterclass',
            name='photo',
            field=models.ImageField(blank=True, upload_to='lessons/', null=True),
        ),
        migrations.AddField(
            model_name='masterclass',
            name='photo_cropping',
            field=image_cropping.fields.ImageRatioField('photo', '500x500', verbose_name='photo cropping', help_text=None, allow_fullsize=False, adapt_rotation=False, hide_image_field=False, size_warning=False, free_crop=False),
        ),
        migrations.AddField(
            model_name='pairedlesson',
            name='photo',
            field=models.ImageField(blank=True, upload_to='lessons/', null=True),
        ),
        migrations.AddField(
            model_name='pairedlesson',
            name='photo_cropping',
            field=image_cropping.fields.ImageRatioField('photo', '500x500', verbose_name='photo cropping', help_text=None, allow_fullsize=False, adapt_rotation=False, hide_image_field=False, size_warning=False, free_crop=False),
        ),
    ]
