from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from api.models import Accommodation, Reservation, Rating
from api.serializers import AccommodationSerializer, ReservationSerializer, RatingSerializer


class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        all_accommodations = Accommodation.objects.all()
        return [acc for acc in all_accommodations if user.university in acc.universities_offered]


    def perform_create(self, serializer):
        data = serializer.validated_data
        existing = Accommodation.objects.filter(
            address=data.get('address'),
            flat_number=data.get('flat_number'),
            floor_number=data.get('floor_number'),
            room_number=data.get('room_number')
        )
        if existing.exists():
            raise PermissionDenied("Duplicate accommodation entry.")

        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    def perform_update(self, serializer):
        serializer.save()

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        return Reservation.objects.filter(created_by__university=user.university)

    def perform_create(self, serializer):
        user = self.request.user
        accommodation = serializer.validated_data['accommodation']

        if user.university not in accommodation.universities_offered:
            raise PermissionDenied("You can only reserve accommodations offered to your university.")

        active_reservations = Reservation.objects.filter(
            accommodation=accommodation,
            status__in=['pending', 'confirmed']
        ).count()

        if active_reservations >= accommodation.beds:
            raise PermissionDenied("This accommodation is fully booked.")

        serializer.save(created_by=user)
        self.notify_staff(accommodation, serializer.validated_data['student_name'], cancelled=False)

    def perform_destroy(self, instance):
        instance.status = 'cancelled'
        instance.save()
        self.notify_staff(instance.accommodation, instance.student_name, cancelled=True)

    def notify_staff(self, accommodation, student_name, cancelled=False):
        subject = f"Reservation {'Cancelled' if cancelled else 'Created'} - {accommodation.title}"
        message = (
            f"Reservation for {student_name} has been {'cancelled' if cancelled else 'created'} for {accommodation.title}\n"
            f"University: {self.request.user.university}"
        )
        uni_email = f"accommodation@{self.request.user.university.lower()}.hk"
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[uni_email],
            fail_silently=True,
        )

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        rating = serializer.save(created_by=user)

        acc = rating.accommodation
        avg = acc.ratings.aggregate(avg=Avg('value'))['avg'] or 0
        acc.rating = round(avg, 2)
        acc.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
