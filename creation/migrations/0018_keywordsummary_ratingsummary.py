# Generated by Django 4.2.11 on 2024-05-07 17:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creation', '0017_alter_creationinfo_creation_method'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeywordSummary',
            fields=[
            ],
            options={
                'verbose_name': 'Most Popular Keywords',
                'verbose_name_plural': 'Most Popular Keyword Stats',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('creation.keyword',),
        ),
        migrations.CreateModel(
            name='RatingSummary',
            fields=[
            ],
            options={
                'verbose_name': 'Rating Summary',
                'verbose_name_plural': 'Rating Summaries',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('creation.creationinfo',),
        ),
    ]
