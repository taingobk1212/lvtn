# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-11-05 08:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_traffic'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Traffic',
        ),
    ]
