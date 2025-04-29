from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from api.models import Reservation, Accommodation
from api.serializers import AccommodationSerializer, ReservationSerializer
from django.db.models import Q
import math, requests
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "university": user.university,
            "role": "staff" if user.is_cedars_staff else "student",
            "token": token.key
        })


class AccommodationFilterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        accommodations = Accommodation.objects.filter(is_available=True)

        accommodations = accommodations.filter(universities_offered__university=user.university)

        property_type = request.GET.get('property_type')
        if property_type:
            accommodations = accommodations.filter(property_type=property_type)

        available_from = request.GET.get('available_from')
        available_to = request.GET.get('available_to')
        if available_from and available_to:
            accommodations = accommodations.filter(
                available_from__lte=available_from,
                available_to__gte=available_to
            )

        min_beds = request.GET.get('min_beds')
        if min_beds:
            accommodations = accommodations.filter(beds__gte=int(min_beds))

        min_bedrooms = request.GET.get('min_bedrooms')
        if min_bedrooms:
            accommodations = accommodations.filter(bedrooms__gte=int(min_bedrooms))

        min_price = request.GET.get('min_price')
        if min_price:
            accommodations = accommodations.filter(price__gte=float(min_price))

        max_price = request.GET.get('max_price')
        if max_price:
            accommodations = accommodations.filter(price__lte=float(max_price))

        room_number = request.GET.get('room_number')
        if room_number:
            accommodations = accommodations.filter(room_number=room_number)

        flat_number = request.GET.get('flat_number')
        if flat_number:
            accommodations = accommodations.filter(flat_number=flat_number)

        floor_number = request.GET.get('floor_number')
        if floor_number:
            accommodations = accommodations.filter(floor_number=floor_number)

        base_lat = request.GET.get('latitude')
        base_lng = request.GET.get('longitude')

        if base_lat and base_lng:
            base_lat = float(base_lat)
            base_lng = float(base_lng)
            accommodations = sorted(
                accommodations,
                key=lambda acc: self.calculate_distance(base_lat, base_lng, float(acc.latitude), float(acc.longitude))
                if acc.latitude and acc.longitude else float('inf')
            )

        serializer = AccommodationSerializer(accommodations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371
        x = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
        y = math.radians(lat2 - lat1)
        return R * math.sqrt(x * x + y * y)


class ReservationFilterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_student:
            reservations = Reservation.objects.filter(student=user)
        elif user.is_cedars_staff:
            reservations = Reservation.objects.filter(accommodation__universities_offered__university=user.university)
        else:
            reservations = Reservation.objects.none()

        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReservationCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        user = request.user

        if user == reservation.student or (user.is_cedars_staff and reservation.accommodation.universities_offered.filter(university=user.university).exists()):
            reservation.status = 'cancelled'
            reservation.save()
            return Response({'message': 'Reservation cancelled.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Not authorized to cancel this reservation.'}, status=status.HTTP_403_FORBIDDEN)
