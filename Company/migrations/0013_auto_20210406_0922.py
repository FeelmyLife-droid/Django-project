# Generated by Django 3.1.7 on 2021-04-06 09:22

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0012_auto_20210406_0919'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='email',
            field=models.EmailField(default=datetime.datetime(2021, 4, 6, 9, 22, 28, 415674, tzinfo=utc), max_length=254),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='company',
            name='slug',
            field=models.SlugField(max_length=100, verbose_name='Название на латинице'),
        ),
    ]
