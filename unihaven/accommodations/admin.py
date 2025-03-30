from django.contrib import admin
from .models import Accommodation, Reservation, Rating
from users.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('is_student', 'is_cedars_staff')}),
    )

admin.site.register(Accommodation)
admin.site.register(Reservation)
admin.site.register(Rating)
