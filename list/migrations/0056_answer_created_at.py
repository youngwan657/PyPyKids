# Generated by Django 2.2.3 on 2019-08-25 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0055_auto_20190824_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='created_at',
            field=models.CharField(blank=True, default=None, max_length=8, null=True),
        ),
    ]
