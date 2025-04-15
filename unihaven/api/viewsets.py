from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg
from api.models import Accommodation, Reservation, Rating
from api.serializers import AccommodationSerializer, ReservationSerializer, RatingSerializer

class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer

    @action(detail=False, methods=['get'], url_path='filter')
    def filter_accommodations(self, request):
        queryset = Accommodation.objects.filter(is_available=True)

        if pt := request.query_params.get("property_type"):
            queryset = queryset.filter(property_type=pt)
        if af := request.query_params.get("available_from"):
            queryset = queryset.filter(available_from__lte=af)
        if at := request.query_params.get("available_to"):
            queryset = queryset.filter(available_to__gte=at)
        if min_beds := request.query_params.get("min_beds"):
            queryset = queryset.filter(beds__gte=int(min_beds))
        if min_bedrooms := request.query_params.get("min_bedrooms"):
            queryset = queryset.filter(bedrooms__gte=int(min_bedrooms))
        if min_price := request.query_params.get("min_price"):
            queryset = queryset.filter(price__gte=float(min_price))
        if max_price := request.query_params.get("max_price"):
            queryset = queryset.filter(price__lte=float(max_price))

        return Response(AccommodationSerializer(queryset, many=True).data)

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating = serializer.save()

        acc = rating.accommodation
        avg = acc.ratings.aggregate(avg=Avg('value'))['avg'] or 0
        acc.rating = round(avg, 2)
        acc.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
