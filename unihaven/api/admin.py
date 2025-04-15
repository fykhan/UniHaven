from django.contrib import admin
from api.models import Accommodation, Reservation, Rating


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'price', 'available_from', 'available_to', 'is_available', 'average_rating')

    def average_rating(self, obj):
        avg = obj.ratings.aggregate_avg('value') or 0
        return round(avg, 2)
    average_rating.short_description = "Rating"

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'student', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('accommodation__title', 'student__username')
    ordering = ('-created_at',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'student', 'value', 'created_at')
    list_filter = ('value',)
    search_fields = ('accommodation__title', 'student__username')
    ordering = ('-created_at',)
