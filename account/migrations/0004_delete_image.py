# Generated by Django 5.0.2 on 2024-03-03 21:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_alter_image_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Image',
        ),
    ]
