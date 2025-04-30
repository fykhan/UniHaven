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
    student = serializers.ReadOnlyField(source='student.username')

    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ['student']

class RatingSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField(source='student.username')
    created_at = serializers.ReadOnlyField()

    class Meta:
        model = Rating
        fields = ['id', 'accommodation', 'student', 'value', 'comment', 'created_at']
        read_only_fields = ['student', 'created_at']
