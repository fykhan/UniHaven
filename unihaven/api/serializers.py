from rest_framework import serializers
from api.models import Accommodation, Reservation, Rating

class AccommodationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'
        depth = 1  # Optional: show full nested accommodation and student info


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

    def validate(self, data):
        student = data.get('student')
        accommodation = data.get('accommodation')
        if Rating.objects.filter(student=student, accommodation=accommodation).exists():
            raise serializers.ValidationError("You have already rated this accommodation.")
        return data
