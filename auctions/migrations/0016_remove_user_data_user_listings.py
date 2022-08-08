# Generated by Django 4.0.6 on 2022-07-28 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_user_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='data',
        ),
        migrations.AddField(
            model_name='user',
            name='listings',
            field=models.ManyToManyField(blank=True, related_name='users', to='auctions.listing'),
        ),
    ]