# Generated by Django 3.1.2 on 2020-10-04 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0020_auto_20201004_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='winners',
            name='listing',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, related_name='winner', to='auctions.listing'),
        ),
    ]
