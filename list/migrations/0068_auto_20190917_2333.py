# Generated by Django 2.2.3 on 2019-09-18 06:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0067_auto_20190917_2330'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quiz',
            options={'ordering': ['-order'], 'verbose_name_plural': 'Quizzes'},
        ),
        migrations.RemoveIndex(
            model_name='quiz',
            name='list_quiz_title_ac5e79_idx',
        ),
    ]
