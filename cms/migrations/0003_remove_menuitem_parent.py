# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-06 15:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0002_auto_20160406_1713'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menuitem',
            name='parent',
        ),
    ]
