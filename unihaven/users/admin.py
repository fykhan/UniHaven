from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, StaffProfile, OwnerProfile, AdminProfile

# Custom User Admin interface that extends Django's default UserAdmin
class CustomUserAdmin(UserAdmin):
    # Fields to display in the user list view
    list_display = ('username', 'email', 'get_full_name', 'phone_number', 'verified', 'get_role')
    
    # Filter options for the right sidebar
    list_filter = ('verified',)
    
    # Fields that can be searched in the admin interface
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    
    # Custom method to display user role in admin list view
    def get_role(self, obj):
        """Returns the user's role as a string for admin display"""
        if obj.is_student():
            return "Student"
        elif obj.is_cedars_staff():
            return "CEDARS Staff"
        elif obj.is_property_owner():
            return "Property Owner"
        elif obj.is_admin():
            return "Admin"
        return "N/A"
    get_role.short_description = 'Role'  # Sets column header in admin

# Inline admin classes for editing profile models directly within User admin
class StudentProfileInline(admin.StackedInline):
    """Allows editing StudentProfile directly within User admin"""
    model = StudentProfile
    can_delete = False  # Prevents profile deletion through this interface
    verbose_name_plural = 'Student Profile'  # Customizes the inline section title

class StaffProfileInline(admin.StackedInline):
    """Inline editor for CEDARS staff profiles"""
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Profile'

class OwnerProfileInline(admin.StackedInline):
    """Inline editor for property owner profiles"""
    model = OwnerProfile
    can_delete = False
    verbose_name_plural = 'Owner Profile'

class AdminProfileInline(admin.StackedInline):
    """Inline editor for admin profiles (no additional fields)"""
    model = AdminProfile
    can_delete = False
    verbose_name_plural = 'Admin Profile'

# Attach all inlines to the CustomUserAdmin
CustomUserAdmin.inlines = [StudentProfileInline, StaffProfileInline, OwnerProfileInline, AdminProfileInline]

# Register models with their admin classes

# Register User model with our custom admin interface
admin.site.register(User, CustomUserAdmin)

# Register profile models with default ModelAdmin
admin.site.register(StudentProfile)  # Enables standalone management of student profiles
admin.site.register(StaffProfile)    # Enables standalone management of staff profiles
admin.site.register(OwnerProfile)    # Enables standalone management of owner profiles
admin.site.register(AdminProfile)    # Enables standalone management of admin profiles
