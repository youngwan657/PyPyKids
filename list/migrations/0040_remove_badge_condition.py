# Generated by Django 2.2.3 on 2019-08-03 02:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0039_auto_20190802_1913'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='badge',
            name='condition',
        ),
    ]
