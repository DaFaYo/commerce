# Generated by Django 4.0.6 on 2022-07-27 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_remove_category_listings_listing_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
