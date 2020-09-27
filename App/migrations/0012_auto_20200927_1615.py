# Generated by Django 3.1 on 2020-09-27 11:15

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('App', '0011_car_used_bonuses'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterModelOptions(
            name='car',
            options={},
        ),
        migrations.AddField(
            model_name='car',
            name='total_bought_litres',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='car',
            name='total_bought_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]