# Generated by Django 2.2.3 on 2019-09-23 08:26

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0078_auto_20190920_0042'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='testcase',
            new_name='input',
        ),
        migrations.AlterField(
            model_name='quiz',
            name='explanation',
            field=ckeditor.fields.RichTextField(blank=True, default='<table border="1" cellpadding="1" cellspacing="1" class="table table-bordered">\n    <tbody>\n        <tr>\n            <td>\n                <p><strong>Block</strong></p>\n            </td>\n        </tr>\n    </tbody>\n</table>\n', null=True),
        ),
    ]
