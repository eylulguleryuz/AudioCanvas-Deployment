# Generated by Django 4.2.11 on 2024-05-11 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0019_alter_creationinfo_creation_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keyword',
            name='keyword',
            field=models.CharField(max_length=100),
        ),
    ]
