# Generated by Django 3.1 on 2020-09-29 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0016_auto_20200929_2058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='quantity_measure',
        ),
        migrations.AddField(
            model_name='productcategory',
            name='quantity_measure',
            field=models.CharField(choices=[('litre', 'Litre'), ('piece', 'Piece'), ('metre', 'Metre'), ('kilogram', 'Kilogram')], default='litre', max_length=31),
            preserve_default=False,
        ),
    ]
