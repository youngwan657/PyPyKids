# Generated by Django 2.2.3 on 2019-08-02 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0035_badge_html'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='visible',
            field=models.BooleanField(default=True),
        ),
    ]