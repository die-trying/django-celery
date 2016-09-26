# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0012_auto_20160910_1235'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_type', models.CharField(choices=[('class', 'Completed class'), ('customer_inspired_cancellation', 'Customer inspired cancellation')], max_length=140)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('originator_id', models.PositiveIntegerField()),
                ('originator_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('teacher', models.ForeignKey(related_name='accounting_events', to='teachers.Teacher')),
            ],
        ),
    ]
