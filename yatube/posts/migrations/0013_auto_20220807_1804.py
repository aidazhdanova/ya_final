# Generated by Django 2.2.16 on 2022-08-07 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_auto_20220807_1759'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created'], 'verbose_name': 'Коментарий', 'verbose_name_plural': 'Коментарии'},
        ),
    ]
