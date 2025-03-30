from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Create User class
class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    is_student = models.BooleanField(default=False)
    is_cedars_staff = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.get_full_name() or self.username}"

    def is_property_owner(self):
        return hasattr(self, 'owner_profile')

    def can_manage_accommodations(self):
        return self.is_cedars_staff() or self.is_admin() or self.is_property_owner()

    def can_make_reservations(self):
        return self.is_student() and self.verified

    def can_view_dashboard(self):
        return self.is_cedars_staff() or self.is_admin()

    class Meta:
        permissions = [
            ("can_manage_accommodations", "Can create/update/delete accommodations"),
            ("can_approve_accommodations", "Can approve accommodation listings"),
            ("can_view_all_reservations", "Can view all reservations"),
            ("can_manage_system", "Can administer the entire system"),
        ]
        
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    hku_id = models.CharField(max_length=10, unique=True)
    faculty = models.CharField(max_length=100, blank=True)
    year_of_study = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(4)])
  
    def __str__(self):
      return f"{self.user} (Student)"

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user} (CEDARS Staff)"
      
class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="owner_profile")
    company_name = models.CharField(max_length=100, blank=True)
    license_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user} (Property Owner)"

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")

    def __str__(self):
        return f"{self.user} (Admin)"

