from rest_framework import serializers
from .models import Accommodation, Reservation, Rating

class AccommodationSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Accommodation
        fields = '__all__'
    
    def get_average_rating(self, obj):
        avg = obj.average_rating()
        return avg if avg is not None else "Not rated"

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
