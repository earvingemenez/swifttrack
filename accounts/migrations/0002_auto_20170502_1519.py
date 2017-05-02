# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-02 07:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payroll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='account',
            name='profile_pic',
            field=models.ImageField(blank=True, upload_to='profiles', verbose_name='Profile picture'),
        ),
        migrations.AddField(
            model_name='payroll',
            name='employee_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]