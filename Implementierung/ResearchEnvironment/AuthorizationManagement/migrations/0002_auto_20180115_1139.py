# Generated by Django 2.0.1 on 2018-01-15 10:39

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0002_logentry_remove_auto_add'),
        ('AuthorizationManagement', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin',
            name='owner_ptr',
        ),
        migrations.RemoveField(
            model_name='owner',
            name='user_ptr',
        ),
        migrations.DeleteModel(
            name='Admin',
        ),
        migrations.DeleteModel(
            name='Owner',
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('AuthorizationManagement.customuser',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('AuthorizationManagement.owner',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]