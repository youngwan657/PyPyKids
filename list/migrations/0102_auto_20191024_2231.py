# Generated by Django 2.2.3 on 2019-10-25 05:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0101_auto_20191020_1027'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ['-modified_date']},
        ),
        migrations.AlterField(
            model_name='answer',
            name='modified_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterIndexTogether(
            name='answer',
            index_together={('date', 'right'), ('modified_date',)},
        ),
    ]
