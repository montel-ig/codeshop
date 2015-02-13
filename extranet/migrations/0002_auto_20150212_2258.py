# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extranet', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='estimated_on',
        ),
        migrations.AddField(
            model_name='issue',
            name='estimated_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='need',
            name='description',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
