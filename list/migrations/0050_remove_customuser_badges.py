# Generated by Django 2.2.3 on 2019-08-24 08:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0049_auto_20190824_0145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='badges',
        ),
    ]