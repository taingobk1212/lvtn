# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-11-28 09:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0014_infointer_appr_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='infointer',
            name='vhc_queue_length',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='infointer',
            name='wait_avrg',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
