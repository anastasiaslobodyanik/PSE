# Generated by Django 2.0 on 2018-03-04 18:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AuthorizationManagement', '0017_auto_20180304_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='description',
            field=models.CharField(blank=True, max_length=250, validators=[django.core.validators.MaxLengthValidator(250)]),
        ),
        migrations.AlterField(
            model_name='resource',
            name='name',
            field=models.CharField(max_length=150, validators=[django.core.validators.MaxLengthValidator(150)]),
        ),
        migrations.AlterField(
            model_name='resource',
            name='type',
            field=models.CharField(max_length=50, validators=[django.core.validators.MaxLengthValidator(50)]),
        ),
    ]
