# Generated by Django 3.1 on 2020-10-10 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0022_auto_20201002_2140'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='daily_car_create_limit',
            field=models.PositiveIntegerField(default=86400),
        ),
    ]
