# Generated by Django 2.2.3 on 2019-08-24 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0053_auto_20190824_0933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
