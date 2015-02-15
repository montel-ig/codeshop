# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extranet', '0004_auto_20150215_0925'),
    ]

    operations = [
        migrations.RenameField(
            model_name='issue',
            old_name='assignee',
            new_name='assignee_login',
        ),
    ]
