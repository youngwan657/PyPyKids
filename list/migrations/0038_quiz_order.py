# Generated by Django 2.2.3 on 2019-08-02 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0037_auto_20190802_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='order',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
        ),
    ]