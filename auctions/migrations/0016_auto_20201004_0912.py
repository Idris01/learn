# Generated by Django 3.1.2 on 2020-10-04 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_auto_20201004_0831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='listing',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='auctions.listing'),
        ),
    ]
