from rest_framework import viewsets, views, status
from rest_framework.response import Response
from accommodations.models import Accommodation, Reservation, Rating
from .serializers import AccommodationSerializer, ReservationSerializer, RatingSerializer
import requests

class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

class AddressLookupView(views.APIView):
    def post(self, request, *args, **kwargs):
        address = request.data.get('address')
        if not address:
            return Response({"error": "Address is required."}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://geodata.gov.hk/gs/api/v1.0.0/locationSearch"
        params = {"q": address, "n": 1}
        response = requests.get(url, params=params)

        if response.status_code != 200 or not response.json():
            return Response({"error": "Location lookup failed."}, status=status.HTTP_502_BAD_GATEWAY)

        data = response.json()[0]
        return Response({
            "latitude": data.get("y"),
            "longitude": data.get("x"),
            "geo_address": data.get("name")
        })
