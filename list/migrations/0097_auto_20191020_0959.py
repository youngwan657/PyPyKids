# Generated by Django 2.2.3 on 2019-10-20 16:59

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0096_auto_20191020_0958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='hint',
            field=ckeditor.fields.RichTextField(blank=True, default=None, null=True),
        ),
    ]