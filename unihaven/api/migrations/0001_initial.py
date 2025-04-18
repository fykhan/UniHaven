# Generated by Django 5.0 on 2025-04-15 08:26

import datetime
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Accommodation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('property_type', models.CharField(choices=[('AP', 'Apartment'), ('HM', 'House - Entire'), ('HR', 'House - Room'), ('SH', 'Shared Room')], max_length=2)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('beds', models.PositiveIntegerField()),
                ('bedrooms', models.PositiveIntegerField()),
                ('address', models.TextField()),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('available_from', models.DateField()),
                ('available_to', models.DateField()),
                ('is_available', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reserved', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_accommodations', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_accommodations', to=settings.AUTH_USER_MODEL)),
                ('reserved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reserved_accommodations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('accommodation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.accommodation')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('accommodation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='api.accommodation')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='given_ratings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('accommodation', 'student')},
            },
        ),
    ]
