# Generated by Django 3.1.7 on 2021-03-10 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0005_auto_20210310_0623'),
        ('Company', '0007_auto_20210310_0624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='bankaccount',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bankaccount', to='bank.bankaccount', verbose_name='Банк'),
        ),
    ]
