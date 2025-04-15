from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Accommodation
from api.serializers import AccommodationSerializer
from django.db.models import Q
import math, requests


class AccommodationFilterView(APIView):
    def get(self, request):
        accommodations = Accommodation.objects.filter(is_available=True)

        # Filters
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

        # Distance Calculation (Optional)
        base_lat = request.GET.get('latitude')
        base_lng = request.GET.get('longitude')

        annotated_data = []
        if base_lat and base_lng:
            base_lat = float(base_lat)
            base_lng = float(base_lng)
            for acc in accommodations:
                if acc.latitude and acc.longitude:
                    distance = self.calculate_distance(base_lat, base_lng, float(acc.latitude), float(acc.longitude))
                else:
                    distance = float('inf')  # Large distance if missing
                annotated_data.append((acc, distance))

            annotated_data.sort(key=lambda x: x[1])
            accommodations = [item[0] for item in annotated_data]

        serializer = AccommodationSerializer(accommodations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        # Equirectangular approximation
        R = 6371  # km
        x = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
        y = math.radians(lat2 - lat1)
        return R * math.sqrt(x * x + y * y)