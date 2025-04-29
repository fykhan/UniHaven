from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import uuid

UNIVERSITY_CHOICES = [
    ('HKU', 'The University of Hong Kong'),
    ('CUHK', 'The Chinese University of Hong Kong'),
    ('HKUST', 'The Hong Kong University of Science and Technology'),
]

class User(AbstractUser):
    UID = models.CharField(max_length=10, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_student = models.BooleanField(default=False)
    is_cedars_staff = models.BooleanField(default=False)
    university = models.CharField(max_length=10, choices=UNIVERSITY_CHOICES, default='HKU')

    def __str__(self):
        return f"{self.get_full_name() or self.username}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.UID:
            self.UID = str(uuid.uuid4())[:10]  # Generate short unique UID
        if not self.phone_number:
            self.phone_number = "0000000000"  # Placeholder, should be prompted via UI

        if self.is_superuser:
            self.is_cedars_staff = True

        super().save(*args, **kwargs)

        if is_new:
            if self.is_student and not hasattr(self, 'student_profile'):
                StudentProfile.objects.create(
                    user=self,
                    university=self.university,
                    UID=self.UID 
                )
            elif self.is_cedars_staff and not hasattr(self, 'staff_profile'):
                StaffProfile.objects.create(
                    user=self,
                    university=self.university
                )

    def can_manage_accommodations(self):
        return self.is_cedars_staff

    def can_make_reservations(self):
        return self.is_student and hasattr(self, 'student_profile')

    def can_view_dashboard(self):
        return self.is_cedars_staff

    def get_user_role(self):
        if hasattr(self, 'student_profile'):
            return 'student'
        elif hasattr(self, 'staff_profile'):
            return 'staff'
        elif hasattr(self, 'admin_profile'):
            return 'admin'
        return 'unknown'

    def clean(self):
        role_count = sum([
            hasattr(self, 'student_profile'),
            hasattr(self, 'staff_profile'),
            hasattr(self, 'admin_profile')
        ])
        if role_count > 1:
            raise ValidationError("A user can only have one profile role (student, staff, admin).")

    class Meta:
        permissions = [
            ("can_manage_accommodations", "Can create/update/delete accommodations"),
            ("can_approve_accommodations", "Can approve accommodation listings"),
            ("can_view_all_reservations", "Can view all reservations"),
            ("can_manage_system", "Can administer the entire system"),
        ]


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    university = models.CharField(max_length=10, choices=UNIVERSITY_CHOICES, default='HKU')
    UID = models.CharField(max_length=10, unique=True)
    # faculty = models.CharField(max_length=100, blank=True)
    # year_of_study = models.PositiveIntegerField(null=True, blank=True, validators=[
    #     MinValueValidator(1), MaxValueValidator(4)
    # ])

    def __str__(self):
        return f"{self.user} (Student)"


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")
    university = models.CharField(max_length=10, choices=UNIVERSITY_CHOICES, default='HKU')
    # department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user} (CEDARS Staff)"


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")

    def __str__(self):
        return f"{self.user} (Admin)"
