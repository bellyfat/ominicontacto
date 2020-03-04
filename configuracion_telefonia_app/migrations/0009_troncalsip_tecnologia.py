# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2019-11-13 20:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracion_telefonia_app', '0008_adiciona_destino_personalizado'),
    ]

    operations = [
        migrations.AddField(
            model_name='troncalsip',
            name='tecnologia',
            field=models.PositiveIntegerField(choices=[(0, 'chansip'), (1, 'pjsip')], default=0),
        ),
    ]