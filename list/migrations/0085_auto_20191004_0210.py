# Generated by Django 2.2.3 on 2019-10-04 09:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0084_auto_20191004_0209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpoint',
            name='pointtype',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='list.PointType'),
        ),
    ]
