# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-15 10:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('navigation', '0012_auto_20170515_1005'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookmark',
            name='book',
        ),
        migrations.RemoveField(
            model_name='history',
            name='bookmarks',
        ),
        migrations.AddField(
            model_name='bookhistory',
            name='bookmarked',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Bookmark',
        ),
    ]
