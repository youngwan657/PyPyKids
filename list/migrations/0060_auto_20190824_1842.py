# Generated by Django 2.2.3 on 2019-08-25 01:42

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0059_auto_20190824_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
