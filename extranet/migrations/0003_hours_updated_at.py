# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extranet', '0002_auto_20150212_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='hours',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
            preserve_default=True,
        ),
    ]
