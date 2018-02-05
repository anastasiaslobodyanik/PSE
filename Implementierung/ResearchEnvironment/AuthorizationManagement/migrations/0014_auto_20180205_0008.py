# Generated by Django 2.0 on 2018-02-04 23:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('AuthorizationManagement', '0013_auto_20180204_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accessrequest',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AuthorizationManagement.Resource'),
        ),
        migrations.AlterField(
            model_name='accessrequest',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AuthorizationManagement.CustomUser'),
        ),
        migrations.AlterField(
            model_name='deletionrequest',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AuthorizationManagement.Resource'),
        ),
        migrations.AlterField(
            model_name='deletionrequest',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AuthorizationManagement.CustomUser'),
        ),
    ]
