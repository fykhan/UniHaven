from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, StudentProfile, StaffProfile, AdminProfile
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.hashers import make_password

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = ('username', 'UID',  'email', 'first_name', 'last_name', 'is_student', 'is_cedars_staff', 'is_superuser')
    list_filter = ('is_student', 'is_cedars_staff', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_student', 'is_cedars_staff', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_student', 'is_cedars_staff', 'is_active'),
        }),
    )

    search_fields = ('username','UID', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    def save_model(self, request, obj, form, change):
        # Set password if not hashed
        if form.cleaned_data.get('password') and not obj.password.startswith('pbkdf2_'):
            obj.password = make_password(form.cleaned_data['password'])
        if not change:
            obj.is_active = True
        super().save_model(request, obj, form, change)
