import requests
import math
from datetime import date, datetime
from django.db import models
from django.db.models import Avg
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import JSONField
from users.models import User

LOCATIONS = {
    "HKU - Main Campus": (22.28405, 114.13784),
    "HKU - Sassoon Road Campus": (22.2675, 114.12881),
    "HKU - Swire Institute of Marine Science": (22.20805, 114.26021),
    "HKU - Kadoorie Centre": (22.43022, 114.11429),
    "HKU - Faculty of Dentistry": (22.28649, 114.14426),
    "HKUST - Main Campus": (22.33584, 114.26355),
    "CUHK - Main Campus": (22.41907, 114.20693),
}

UNIVERSITY_CHOICES = [
    ('HKU', 'The University of Hong Kong'),
    ('CUHK', 'The Chinese University of Hong Kong'),
    ('HKUST', 'The Hong Kong University of Science and Technology'),
]

def calculate_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    x = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    y = math.radians(lat2 - lat1)
    distance = 6371 * math.sqrt(x*x + y*y)  # Distance in kilometers
    return round(distance, 2)

def lookup_coordinates_and_geoaddress(address):
    url = "https://www.als.gov.hk/lookup"
    params = {"q": address, "output": "JSON"}
    headers = {"Accept": "application/json"}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        suggestions = data.get("SuggestedAddress")
        if not suggestions:
            print("No address found.")
            return None, None, ""
        premises = suggestions[0]['Address']['PremisesAddress']
        geo_info = premises['GeospatialInformation']
        lat = float(geo_info['Latitude'])
        lon = float(geo_info['Longitude'])
        geo_address = premises.get("GeoAddress", "")
        return lat, lon, geo_address
    except Exception as e:
        print(f"[ALS Lookup Error] {e}")
        return None, None, ""

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
    room_number = models.CharField(max_length=10, null=True, blank=True)
    flat_number = models.CharField(max_length=10)
    floor_number = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geo_address = models.CharField(max_length=50, blank=True, null=True)
    available_from = models.DateField()
    available_to = models.DateField()
    is_available = models.BooleanField(default=True)
    universities_offered = models.JSONField(default=list)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_accommodations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reserved = models.BooleanField(default=False)
    reserved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reserved_accommodations')
    campus_distances = JSONField(default=dict)

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude or not self.geo_address:
            lat, lon, geo_addr = lookup_coordinates_and_geoaddress(self.address)
            self.latitude = lat
            self.longitude = lon
            self.geo_address = geo_addr

        if self.latitude and self.longitude and self.universities_offered:
            self.campus_distances = {}
            for label, (lat_campus, lon_campus) in LOCATIONS.items():
                if any(label.startswith(uni) for uni in self.universities_offered):
                    self.campus_distances[label] = calculate_distance(
                        self.latitude, self.longitude, lat_campus, lon_campus
                    )

        super().save(*args, **kwargs)

    def average_rating(self):
        ratings = self.ratings.all()
        total = sum(r.value for r in ratings)
        count = ratings.count()
        return round(total / count, 2) if count > 0 else 0

    def __str__(self):
        return f"{self.title} - {self.get_property_type_display()}"

    class Meta:
        unique_together = ('geo_address', 'flat_number', 'floor_number', 'room_number')

class Reservation(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ])
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)

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

    def __str__(self):
        return f"Reservation #{self.id} - {self.accommodation.title}"

class Rating(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='ratings')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    value = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('accommodation', 'student')

    def __str__(self):
        return f"{self.value} stars for {self.accommodation.title}"
