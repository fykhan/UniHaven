from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, StaffProfile, AdminProfile

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('UID', 'phone_number', 'is_student', 'is_cedars_staff', 'university')
        }),
    )
    list_display = ('username', 'email', 'is_student', 'is_cedars_staff', 'university')
    list_filter = ('is_student', 'is_cedars_staff', 'university')

admin.site.register(User, UserAdmin)
admin.site.register(StudentProfile)
admin.site.register(StaffProfile)
admin.site.register(AdminProfile)
