# Generated by Django 3.1 on 2020-10-10 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0023_config_daily_car_create_limit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='daily_car_create_limit',
            field=models.PositiveIntegerField(default=3),
        ),
    ]
