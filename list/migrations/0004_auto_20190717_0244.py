# Generated by Django 2.2.3 on 2019-07-17 09:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0003_auto_20190717_0240'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='writer',
            new_name='name',
        ),
    ]
