# Generated by Django 5.0 on 2025-04-15 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accommodation',
            name='campus_distances',
            field=models.JSONField(default=dict),
        ),
    ]
