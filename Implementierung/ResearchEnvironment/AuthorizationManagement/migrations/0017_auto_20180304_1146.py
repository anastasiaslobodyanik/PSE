# Generated by Django 2.0 on 2018-03-04 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AuthorizationManagement', '0016_auto_20180304_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='name',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='resource',
            name='type',
            field=models.CharField(max_length=50),
        ),
    ]
