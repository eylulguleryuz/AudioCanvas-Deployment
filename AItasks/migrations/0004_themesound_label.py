# Generated by Django 4.2.11 on 2024-05-11 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AItasks', '0003_themesound'),
    ]

    operations = [
        migrations.AddField(
            model_name='themesound',
            name='label',
            field=models.CharField(default='funny', max_length=100),
            preserve_default=False,
        ),
    ]
