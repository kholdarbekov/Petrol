# Generated by Django 3.1 on 2020-09-24 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0010_auto_20200919_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='used_bonuses',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
