# Generated by Django 5.0 on 2025-04-15 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_accommodation_campus_distances'),
    ]

    operations = [
        migrations.AddField(
            model_name='accommodation',
            name='geo_address',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
