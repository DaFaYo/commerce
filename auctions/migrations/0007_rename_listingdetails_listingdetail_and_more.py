# Generated by Django 4.0.6 on 2022-07-15 14:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_category_listingdetails'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ListingDetails',
            new_name='ListingDetail',
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'categories'},
        ),
    ]