from django.contrib import admin
from api.models import Accommodation, Reservation, Rating

@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'price', 'available_from', 'available_to', 'is_available', 'average_rating')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'student_name', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('accommodation__title', 'student_name')
    ordering = ('-created_at',)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'student_name', 'value', 'created_at')
    list_filter = ('value',)
    search_fields = ('accommodation__title', 'student_name')
    ordering = ('-created_at',)
