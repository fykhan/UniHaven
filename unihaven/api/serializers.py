from rest_framework import serializers
from api.models import Accommodation, Reservation, Rating

class AccommodationSerializer(serializers.ModelSerializer):
    geo_address = serializers.CharField(read_only=True)
    campus_distances = serializers.JSONField(read_only=True)
    created_by = serializers.ReadOnlyField(source='created_by.username')
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Accommodation
        fields = '__all__'
        read_only_fields = ['created_by']
        unique_together = ('geo_address', 'flat_number', 'floor_number', 'room_number')

class ReservationSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ['created_by']

class RatingSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    created_at = serializers.ReadOnlyField()

    class Meta:
        model = Rating
        unique_together = ('accommodation', 'student_name')
        fields = ['id', 'accommodation', 'student_name', 'value', 'comment', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']
