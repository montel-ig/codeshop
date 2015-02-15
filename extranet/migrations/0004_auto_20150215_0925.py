# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extranet', '0003_hours_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='assignee',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='need',
            name='description',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
    ]
