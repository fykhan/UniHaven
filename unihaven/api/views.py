from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django.db.models import Q
from django.shortcuts import get_object_or_404
import math
from datetime import datetime

from api.models import Reservation, Accommodation, LOCATIONS
from api.serializers import AccommodationSerializer, ReservationSerializer

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get(self, request):
        user = request.user
        return Response({
            "university": user.university,
            "role": "staff"
        })

class AccommodationFilterView(APIView):
    permission_classes = [IsAuthenticated]

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        from math import radians, cos, sqrt
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
        x = radians(lon2 - lon1) * cos(radians((lat1 + lat2) / 2))
        y = radians(lat2 - lat1)
        distance = 6371 * sqrt(x * x + y * y)  # in km
        return round(distance, 2)

    def get_university_from_request(self, request):
        if request.user and request.user.is_authenticated:
            return getattr(request.user, 'university', None)
        token_university = getattr(request, 'university', None)
        return token_university

    def get(self, request):
        user_university = self.get_university_from_request(request)
        if not user_university:
            return Response({"error": "University context is missing."}, status=403)

        accommodations = Accommodation.objects.filter(
            is_available=True,
            reserved=False,
            universities_offered__name=user_university
        ).distinct()

        property_type = request.GET.get("property_type")
        if property_type:
            accommodations = accommodations.filter(property_type=property_type)

        available_from = request.GET.get("available_from")
        available_to = request.GET.get("available_to")
        if available_from and available_to:
            try:
                available_from = datetime.strptime(available_from, "%Y-%m-%d").date()
                available_to = datetime.strptime(available_to, "%Y-%m-%d").date()
                accommodations = accommodations.filter(
                    available_from__lte=available_from,
                    available_to__gte=available_to
                )
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        min_beds = request.GET.get("min_beds")
        if min_beds:
            accommodations = accommodations.filter(beds__gte=int(min_beds))

        min_bedrooms = request.GET.get("min_bedrooms")
        if min_bedrooms:
            accommodations = accommodations.filter(bedrooms__gte=int(min_bedrooms))

        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        if min_price and max_price:
            accommodations = accommodations.filter(
                price__gte=float(min_price), price__lte=float(max_price)
            )

        campus_label = request.GET.get("campus_label")
        max_distance = request.GET.get("max_distance")
        if campus_label and campus_label in LOCATIONS:
            base_lat, base_lng = LOCATIONS[campus_label]
            accommodations = sorted(
                accommodations,
                key=lambda acc: self.calculate_distance(base_lat, base_lng, float(acc.latitude), float(acc.longitude))
                if acc.latitude and acc.longitude else float('inf')
            )
            if max_distance:
                max_distance = float(max_distance)
                accommodations = [
                    acc for acc in accommodations
                    if self.calculate_distance(base_lat, base_lng, float(acc.latitude), float(acc.longitude)) <= max_distance
                ]

        serializer = AccommodationSerializer(accommodations, many=True)
        return Response(serializer.data)
    
class ReservationFilterView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get(self, request):
        user = request.user
        reservations = Reservation.objects.filter(created_by__university=user.university)
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReservationCancelView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def delete(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        user = request.user

        if reservation.created_by.university == user.university:
            reservation.status = 'cancelled'
            reservation.save()
            return Response({'message': 'Reservation cancelled.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Not authorized to cancel this reservation.'}, status=status.HTTP_403_FORBIDDEN)
