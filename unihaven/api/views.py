from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Accommodation
from api.serializers import AccommodationSerializer
from django.db.models import Q

class AddressLookupView(APIView):
    def post(self, request):
        address = request.data.get('address')
        if not address:
            return Response({"error": "Address is required."}, status=400)

        url = "https://geodata.gov.hk/gs/api/v1.0.0/locationSearch"
        params = {"q": address, "n": 1}
        response = requests.get(url, params=params)

        if response.status_code != 200 or not response.json():
            return Response({"error": "Location lookup failed."}, status=502)

        data = response.json()[0]
        return Response({
            "latitude": data.get("y"),
            "longitude": data.get("x"),
            "geo_address": data.get("name")
        })

class AccommodationFilterView(APIView):
    def get(self, request):
        accommodations = Accommodation.objects.filter(is_available=True)
        print(request.GET)
        # Property type
        property_type = request.GET.get('property_type')
        if property_type:
            accommodations = accommodations.filter(property_type=property_type)

        # Availability period
        available_from = request.GET.get('available_from')
        available_to = request.GET.get('available_to')
        if available_from and available_to:
            accommodations = accommodations.filter(
                available_from__lte=available_from,
                available_to__gte=available_to
            )

        # Min beds
        min_beds = request.GET.get('min_beds')
        if min_beds:
            accommodations = accommodations.filter(beds__gte=int(min_beds))

        # Min bedrooms
        min_bedrooms = request.GET.get('min_bedrooms')
        if min_bedrooms:
            accommodations = accommodations.filter(bedrooms__gte=int(min_bedrooms))

        # Price range
        min_price = request.GET.get('min_price')
        if min_price:
            accommodations = accommodations.filter(price__gte=float(min_price))

        max_price = request.GET.get('max_price')
        if max_price:
            accommodations = accommodations.filter(price__lte=float(max_price))

        serializer = AccommodationSerializer(accommodations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)