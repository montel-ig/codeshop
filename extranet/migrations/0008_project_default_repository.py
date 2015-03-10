# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extranet', '0007_auto_20150304_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='default_repository',
            field=models.ForeignKey(blank=True, to='extranet.Repository', null=True),
            preserve_default=True,
        ),
    ]
