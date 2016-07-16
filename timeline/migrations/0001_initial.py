# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    # replaces = [('timeline', '0001_initial'), ('timeline', '0002_auto_20160701_2213'), ('timeline', '0003_auto_20160702_0735'), ('timeline', '0004_entry_duration'), ('timeline', '0005_auto_20160713_1548'), ('timeline', '0006_auto_20160713_1622'), ('timeline', '0007_auto_20160714_1053'), ('timeline', '0008_entry_active'), ('timeline', '0009_auto_20160716_0413')]

    dependencies = [
        ('crm', '0002_auto_20160701_0448'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('slots', models.SmallIntegerField(default=1)),
                ('taken_slots', models.SmallIntegerField(default=0)),
                ('lesson_id', models.PositiveIntegerField(blank=True, null=True)),
                ('lesson_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='timeline_entries', to=settings.AUTH_USER_MODEL)),
                ('customers', models.ManyToManyField(blank=True, related_name='planned_timeline_entries', to='crm.Customer')),
                ('active', models.SmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active')], default=1)),
            ],
        ),
        migrations.AlterModelOptions(
            name='entry',
            options={'verbose_name_plural': 'Entries'},
        ),
        migrations.AlterModelOptions(
            name='entry',
            options={'permissions': (('other_entries', "Can work with other's timeleine entries"),), 'verbose_name_plural': 'Entries'},
        ),
    ]
