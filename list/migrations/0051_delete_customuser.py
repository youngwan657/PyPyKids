# Generated by Django 2.2.3 on 2019-08-24 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0050_remove_customuser_badges'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
