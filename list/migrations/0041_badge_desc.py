# Generated by Django 2.2.3 on 2019-08-03 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0040_remove_badge_condition'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='desc',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
