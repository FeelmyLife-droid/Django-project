# Generated by Django 3.1.7 on 2021-05-27 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0012_auto_20210526_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailbank',
            name='publication_mail',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='mailbank',
            name='date_mail',
            field=models.DateTimeField(null=True),
        ),
    ]
