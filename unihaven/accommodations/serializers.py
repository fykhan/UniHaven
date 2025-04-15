from rest_framework import serializers
from api.models import Accommodation, Reservation, Rating
from django.db.models import Avg

class AccommodationSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Accommodation
        fields = '__all__'

    def get_average_rating(self, obj):
        avg = obj.ratings.aggregate(avg=Avg('value'))['avg'] or 0
        return round(avg, 2)


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'


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
