# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import extranet.models.utils


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Hours',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('amount', models.DecimalField(max_digits=4, decimal_places=2)),
                ('start_time', models.TimeField(null=True, blank=True)),
                ('end_time', models.TimeField(null=True, blank=True)),
                ('comment', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('input_data_json', models.TextField(null=True, blank=True)),
                ('coder', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Hours',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HourTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, extranet.models.utils.HoursReporter),
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('synced_at', models.DateTimeField(null=True, blank=True)),
                ('number', models.IntegerField()),
                ('title', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(null=True)),
                ('updated_at', models.DateTimeField(null=True)),
                ('closed_at', models.DateTimeField(null=True, blank=True)),
                ('html_url', models.URLField(null=True)),
                ('estimated_hours', models.DecimalField(null=True, max_digits=3, decimal_places=1, blank=True)),
                ('estimated_on', models.DateField(null=True, blank=True)),
                ('work_initiated_at', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Github issue',
            },
            bases=(models.Model, extranet.models.utils.HoursReporter),
        ),
        migrations.CreateModel(
            name='Need',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_estimate_requested', models.BooleanField(default=False)),
                ('estimate_finished_at', models.DateTimeField(default=None, null=True, blank=True)),
                ('estimate_approved_at', models.DateTimeField(default=None, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model, extranet.models.utils.HoursReporter),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('login', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Github organization',
            },
            bases=(models.Model, extranet.models.utils.HoursReporter),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('coder_team', models.ForeignKey(related_name='customer_projects', to='auth.Group')),
                ('customer_team', models.ForeignKey(related_name='code_projects', to='auth.Group')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, extranet.models.utils.HoursReporter),
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('synced_at', models.DateTimeField(null=True, blank=True)),
                ('name', models.CharField(max_length=100)),
                ('default_project', models.ForeignKey(blank=True, to='extranet.Project', null=True)),
                ('organization', models.ForeignKey(to='extranet.Organization')),
            ],
            options={
                'verbose_name': 'Github repository',
                'verbose_name_plural': 'Github repositories',
            },
            bases=(models.Model, extranet.models.utils.HoursReporter),
        ),
        migrations.AddField(
            model_name='need',
            name='project',
            field=models.ForeignKey(to='extranet.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='issue',
            name='need',
            field=models.ForeignKey(blank=True, to='extranet.Need', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='issue',
            name='repository',
            field=models.ForeignKey(to='extranet.Repository'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hours',
            name='issue',
            field=models.ForeignKey(blank=True, to='extranet.Issue', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hours',
            name='project',
            field=models.ForeignKey(to='extranet.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hours',
            name='repository',
            field=models.ForeignKey(blank=True, to='extranet.Repository', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hours',
            name='tags',
            field=models.ManyToManyField(to='extranet.HourTag'),
            preserve_default=True,
        ),
    ]
