# Generated by Django 2.2.3 on 2019-08-03 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_goods_ppid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='ppid',
            field=models.CharField(max_length=5),
        ),
    ]