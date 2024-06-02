# Generated by Django 4.2.11 on 2024-03-11 08:50

import creation.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CreationInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SoundClip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sound_file', models.FileField(upload_to=creation.models.upload_location_sounds)),
                ('creation_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='creation.creationinfo')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('creation_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='creation.creationinfo')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_file', models.ImageField(upload_to=creation.models.upload_location_images)),
                ('creation_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='creation.creationinfo')),
            ],
        ),
        migrations.CreateModel(
            name='Customization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.PositiveIntegerField()),
                ('creation_method', models.CharField(max_length=255)),
                ('creation_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='creation.creationinfo')),
            ],
        ),
    ]
