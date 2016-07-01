# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm', '0002_auto_20160701_0448'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('start_time', models.DateTimeField()),
                ('slots', models.SmallIntegerField(default=1)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True, related_name='timeline_entries', blank=True)),
                ('customers', models.ManyToManyField(to='crm.Customer', related_name='planned_timeline_entries', blank=True))
            ],
        ),
        migrations.AlterModelOptions(
            name='entry',
            options={'verbose_name_plural': 'Entries'},
        ),
        migrations.AddField(
            model_name='entry',
            name='event_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='entry',
            name='event_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='entry',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, related_name='timeline_entries'),
        ),
        migrations.AddField(
            model_name='entry',
            name='taken_slots',
            field=models.SmallIntegerField(default=0),
        ),
    ]
