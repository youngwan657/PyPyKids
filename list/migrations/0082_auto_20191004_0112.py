# Generated by Django 2.2.3 on 2019-10-04 08:12

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0081_auto_20191001_2042'),
    ]

    operations = [
        migrations.CreateModel(
            name='PointType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('point', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='customuser',
            name='score',
            field=models.IntegerField(default=100),
        ),
        migrations.CreateModel(
            name='UserPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.IntegerField(default=0)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('customuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='list.CustomUser')),
                ('point_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='list.PointType')),
            ],
        ),
    ]
