from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from datetime import date, datetime
from django.db.models import Avg

# Create your models here.
class Accommodation(models.Model):
    PROPERTY_TYPES = [
        ('AP', 'Apartment'),
        ('HM', 'House - Entire'),
        ('HR', 'House - Room'),
        ('SH', 'Shared Room'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=2, choices=PROPERTY_TYPES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    beds = models.PositiveIntegerField()
    bedrooms = models.PositiveIntegerField()
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    available_from = models.DateField()
    available_to = models.DateField()
    is_available = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_accommodations')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_accommodations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reserved = models.BooleanField(default=False)
    reserved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reserved_accommodations')

    def average_rating(self):
        ratings = self.ratings.all()
        total = sum(r.value for r in ratings)
        count = ratings.count()
        return round(total / count, 2) if count > 0 else 0

    def __str__(self):
        return f"{self.title} - {self.get_property_type_display()}"


class Reservation(models.Model):
    student = models.ForeignKey('users.User', on_delete=models.CASCADE)
    accommodation = models.ForeignKey('Accommodation', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ])

    def update_status(self):
        today = date.today()
        if self.status in ['cancelled', 'completed']:
            return

        if self.end_date < today:
            self.status = 'completed'
        elif self.start_date <= today <= self.end_date:
            self.status = 'confirmed'
        else:
            self.status = 'pending'
        self.save()
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reservation #{self.id} - {self.accommodation.title}"


class Rating(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='ratings')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    value = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('accommodation', 'student')

    def __str__(self):
        return f"{self.value} stars for {self.accommodation.title}"
    
