# Generated by Django 3.1.7 on 2021-04-06 09:04

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0009_auto_20210310_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='slug',
            field=models.CharField(default=datetime.datetime(2021, 4, 6, 9, 4, 14, 242517, tzinfo=utc), max_length=100, verbose_name='Название на латинице'),
            preserve_default=False,
        ),
    ]