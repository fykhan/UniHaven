from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from api.models import Accommodation, Reservation, Rating
from api.serializers import AccommodationSerializer, ReservationSerializer, RatingSerializer
from rest_framework.permissions import IsAuthenticated

class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        student_id = self.request.query_params.get("student")
        if student_id:
            return Reservation.objects.filter(student__id=student_id)
        return super().get_queryset()

    @action(detail=True, methods=['get', 'post'], url_path='', url_name='by_accommodation')
    def reservation_by_accommodation(self, request, pk=None):
        accommodation = Accommodation.objects.filter(pk=pk).first()
        if not accommodation:
            return Response({'error': 'Accommodation not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            reservations = Reservation.objects.filter(accommodation=accommodation)
            serializer = ReservationSerializer(reservations, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            data = request.data.copy()
            data['accommodation'] = accommodation.id
            data['student'] = request.user.id
            serializer = ReservationSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def create(self, request, *args, **kwargs):
        student = request.data.get('student')
        accommodation = request.data.get('accommodation')

        if Rating.objects.filter(student=student, accommodation=accommodation).exists():
            return Response({'error': 'You have already rated this accommodation.'}, status=400)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating = serializer.save()

        acc = rating.accommodation
        avg = acc.ratings.aggregate(avg=Avg('value'))['avg'] or 0
        acc.rating = round(avg, 2)
        acc.save()

        return Response(serializer.data, status=201)
