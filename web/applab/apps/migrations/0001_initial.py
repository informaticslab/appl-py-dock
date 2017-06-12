# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import apps.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AndroidProject',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('application_id', models.CharField(max_length=100, default='')),
                ('google_play_link', models.URLField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='IosProject',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('bundle_id', models.CharField(max_length=100, default='')),
                ('apple_app_store_link', models.URLField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('project_code_name', models.SlugField(max_length=30)),
                ('is_archived', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectOverview',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('platform', models.CharField(choices=[('', 'No Platform'), ('ios', 'iOS'), ('and', 'Android'), ('win', 'Windows Mobile'), ('mlp', 'Multi-Platform')], max_length=3, default='')),
                ('major_version', models.PositiveSmallIntegerField()),
                ('minor_version', models.PositiveSmallIntegerField()),
                ('date_published', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('icon', models.ImageField(upload_to=apps.models.overview_icon_upload_path)),
                ('source_code_link', models.URLField(blank=True, default='')),
                ('project', models.ForeignKey(to='apps.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectOverviewScreenshot',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('screenshot', models.ImageField(upload_to=apps.models.overview_screenshot_upload_path)),
                ('project_overview', models.ForeignKey(to='apps.ProjectOverview', related_name='screenshots')),
            ],
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('major_version', models.PositiveSmallIntegerField()),
                ('minor_version', models.PositiveSmallIntegerField()),
                ('point_version', models.PositiveSmallIntegerField()),
                ('build_version', models.PositiveSmallIntegerField()),
                ('is_archived', models.BooleanField(default=False)),
                ('what_is_new', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('is_featured_release', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AndroidRelease',
            fields=[
                ('release_ptr', models.OneToOneField(to='apps.Release', primary_key=True, auto_created=True, parent_link=True, serialize=False)),
                ('apk_file', models.FileField(upload_to=apps.models.apk_upload_path)),
            ],
            bases=('apps.release',),
        ),
        migrations.CreateModel(
            name='IosRelease',
            fields=[
                ('release_ptr', models.OneToOneField(to='apps.Release', primary_key=True, auto_created=True, parent_link=True, serialize=False)),
                ('ipa_file', models.FileField(upload_to=apps.models.ipa_upload_path)),
            ],
            bases=('apps.release',),
        ),
        migrations.AddField(
            model_name='iosproject',
            name='project_overview',
            field=models.ForeignKey(to='apps.ProjectOverview'),
        ),
        migrations.AddField(
            model_name='androidproject',
            name='project_overview',
            field=models.ForeignKey(to='apps.ProjectOverview'),
        ),
        migrations.AddField(
            model_name='iosrelease',
            name='ios_project',
            field=models.ForeignKey(to='apps.IosProject'),
        ),
        migrations.AddField(
            model_name='androidrelease',
            name='android_project',
            field=models.ForeignKey(to='apps.AndroidProject'),
        ),
    ]
