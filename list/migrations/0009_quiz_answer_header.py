# Generated by Django 2.2.3 on 2019-07-18 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0008_auto_20190717_2320'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='answer_header',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]