# Generated by Django 3.1.7 on 2021-03-14 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0006_auto_20210310_2040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='token',
            field=models.TextField(verbose_name='Токен'),
        ),
    ]
