# Generated by Django 2.2.3 on 2019-09-07 22:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0062_good'),
    ]

    operations = [
        migrations.RenameField(
            model_name='good',
            old_name='value',
            new_name='score',
        ),
    ]
