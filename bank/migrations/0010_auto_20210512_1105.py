# Generated by Django 3.1.7 on 2021-05-12 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0009_auto_20210423_1229'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bankaccount',
            options={'ordering': ['bank_id'], 'verbose_name': 'Аккаунт', 'verbose_name_plural': 'Аккаунты'},
        ),
    ]