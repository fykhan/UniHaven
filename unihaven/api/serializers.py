from rest_framework import serializers
from api.models import Accommodation, Reservation, Rating

class AccommodationSerializer(serializers.ModelSerializer):
    geo_address = serializers.CharField(read_only=True)
    campus_distances = serializers.JSONField(read_only=True)

    class Meta:
        model = Accommodation
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
