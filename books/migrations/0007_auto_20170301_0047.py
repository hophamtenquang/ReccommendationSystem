# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-01 00:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_auto_20170226_2246'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='publication_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='publisher',
            field=models.CharField(max_length=120, null=True),
        ),
    ]
