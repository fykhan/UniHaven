from django.db import models
from djang0.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Create User class
class User(AbstractUser):
  phone_number = models.CharField(max_length=15, blank=True)

  def __str__(self):
    return f"{self.get_full_name()} ({self.get_role_display()})"

  def is_student(self):
    return self.role == self.Role.STUDENT

  def is_staff_member(self):
      return self.role == self.Role.STAFF

  def is_admin(self):
      return self.role == self.Role.ADMIN

# Add custom permissions
class Meta:
    permissions = [
        ("manage_accommodations", "Can create, update, and delete accommodations"),
        ("manage_reservations", "Can manage all reservations"),
        ("view_all_reservations", "Can view all reservations"),
    ]
