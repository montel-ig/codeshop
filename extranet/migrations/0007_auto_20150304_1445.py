# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extranet', '0006_timer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='hours',
            name='coder_billing_month',
            field=models.ForeignKey(related_name='billable_coder_hours', blank=True, to='extranet.Month', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hours',
            name='project_billing_month',
            field=models.ForeignKey(related_name='billable_project_hours', blank=True, to='extranet.Month', null=True),
            preserve_default=True,
        ),
    ]
