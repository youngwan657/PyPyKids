# Generated by Django 2.2.3 on 2019-10-20 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0091_auto_20191020_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='answer',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='answer',
            name='expected_output',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='answer',
            name='expected_stdout',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='answer',
            name='input',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='answer',
            name='output',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='answer',
            name='stdout',
            field=models.TextField(default=''),
        ),
    ]