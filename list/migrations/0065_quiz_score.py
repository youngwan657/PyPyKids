# Generated by Django 2.2.3 on 2019-09-08 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0064_auto_20190907_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]