# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('extranet', '0005_auto_20150215_0929'),
    ]

    operations = [
        migrations.CreateModel(
            name='Timer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('date', models.DateField(null=True, blank=True)),
                ('amount', models.DecimalField(null=True, max_digits=4, decimal_places=2, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('coder', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
                ('issue', models.ForeignKey(blank=True, to='extranet.Issue', null=True)),
                ('project', models.ForeignKey(blank=True, to='extranet.Project', null=True)),
                ('repository', models.ForeignKey(blank=True, to='extranet.Repository', null=True)),
                ('tags', models.ManyToManyField(to='extranet.HourTag', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
