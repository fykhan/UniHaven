from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Accommodation, Reservation, Rating
from .serializers import AccommodationSerializer, ReservationSerializer, RatingSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q

class AccommodationList(APIView):
    """
    GET: Search and return a list of accommodation based on the query parameters.
    """
    def get(self, request):
        # Example Parameters：?type=APARTMENT&min_price=5000&max_price=10000
        acc_type = request.query_params.get('type', None)
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        # You can continue to add other filtering conditions, such as number of beds, distance, etc.
        
        accommodations = Accommodation.objects.all()
        if acc_type:
            accommodations = accommodations.filter(accommodation_type=acc_type)
        if min_price:
            accommodations = accommodations.filter(price__gte=min_price)
        if max_price:
            accommodations = accommodations.filter(price__lte=max_price)
            
        serializer = AccommodationSerializer(accommodations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateReservation(APIView):
    """
    POST: Create a reservation for a specific property.
    """
    def post(self, request):
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            accommodation_id = serializer.validated_data['accommodation'].id
            # Check if the same accommodation has already been booked
            existing = Reservation.objects.filter(accommodation_id=accommodation_id, status='RESERVED')
            if existing.exists():
                return Response({'error': 'Accommodation is already reserved.'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CancelReservation(APIView):
    """
    POST: Cancel an existing reservation.
    """
    def post(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, id=reservation_id)
        if reservation.status != 'RESERVED':
            return Response({'error': 'Reservation cannot be cancelled.'},
                            status=status.HTTP_400_BAD_REQUEST)
        reservation.status = 'CANCELLED'
        reservation.save()
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateAccommodation(APIView):
    """
    POST: New accommodation information is added by CEDARS accommodation specialists.
    """
    def post(self, request):
        serializer = AccommodationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RateAccommodation(APIView):
    """
    POST: Users rate accommodation.
    """
    def post(self, request):
        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            # Check if the user has rated this accommodation
            user = serializer.validated_data['user']
            accommodation = serializer.validated_data['accommodation']
            if Rating.objects.filter(user=user, accommodation=accommodation).exists():
                return Response({'error': 'You have already rated this accommodation.'},
                                status=status.HTTP_400_BAD_REQUEST)
            rating = serializer.save()
            # Update accommodation's overall rating and count
            accommodation.total_rating += rating.score
            accommodation.rating_count += 1
            accommodation.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
