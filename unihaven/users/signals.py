# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, StudentProfile, StaffProfile
from rest_framework.authtoken.models import Token
from django.conf import settings

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_student and not hasattr(instance, 'student_profile'):
            StudentProfile.objects.create(
                user=instance,
                university=instance.university,
                UID=instance.UID or instance.username[:10]
            )
        elif instance.is_cedars_staff and not hasattr(instance, 'staff_profile'):
            StaffProfile.objects.create(
                user=instance,
                university=instance.university
            )
        print("[Signals] User post_save signal loaded.")

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)