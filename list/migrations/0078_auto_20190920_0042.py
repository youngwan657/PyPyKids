# Generated by Django 2.2.3 on 2019-09-20 07:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0077_auto_20190919_2104'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testcase',
            old_name='test',
            new_name='input',
        ),
    ]
