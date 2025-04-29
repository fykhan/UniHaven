from rest_framework import serializers
from api.models import Accommodation, Reservation, Rating

class AccommodationSerializer(serializers.ModelSerializer):
    geo_address = serializers.CharField(read_only=True)
    campus_distances = serializers.JSONField(read_only=True)
    created_by = serializers.ReadOnlyField(source='created_by.username')  # or just ReadOnlyField()
    class Meta:
        model = Accommodation
        fields = '__all__'
        read_only_fields = ['created_by']


class ReservationSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField(source='student.username')

    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ['student']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
