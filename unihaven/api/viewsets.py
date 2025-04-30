from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from api.models import Accommodation, Reservation, Rating
from api.serializers import AccommodationSerializer, ReservationSerializer, RatingSerializer
from users.models import User

class AccommodationViewSet(viewsets.ModelViewSet):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        return [
            acc for acc in Accommodation.objects.all()
            if user.university in acc.universities_offered
        ]

    def perform_create(self, serializer):
        if not self.request.user.is_cedars_staff:
            raise PermissionDenied("Only university staff can add accommodations.")

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
        if not self.request.user.is_cedars_staff:
            raise PermissionDenied("Only university staff can delete accommodations.")
        instance.delete()

    def perform_update(self, serializer):
        if not self.request.user.is_cedars_staff:
            raise PermissionDenied("Only university staff can update accommodations.")
        serializer.save()

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            return Reservation.objects.filter(student=user)
        elif user.is_cedars_staff:
            return [
                r for r in Reservation.objects.all()
                if r.student.university == user.university
            ]
        return []

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

        serializer.save(student=user)
        self.notify_staff(accommodation, user)

    def perform_destroy(self, instance):
        user = self.request.user
        if user == instance.student or (user.is_cedars_staff and instance.student.university == user.university):
            instance.status = 'cancelled'
            instance.save()
            self.notify_staff(instance.accommodation, instance.student, cancelled=True)
            return
        raise PermissionDenied("Not authorized to cancel this reservation.")

    def notify_staff(self, accommodation, student, cancelled=False):
        staff_users = User.objects.filter(is_cedars_staff=True, university=student.university)
        emails = [s.email for s in staff_users if s.email]
        if emails:
            action = "cancelled" if cancelled else "made"
            subject = f"Reservation {action.capitalize()} Notification"
            message = (
                f"A reservation has been {action} by {student.first_name} {student.last_name} ({student.username}); UID: {student.UID} for: {accommodation.title}\n"
                f"University: {student.university}\n"
                f"Reservation status: {'Cancelled' if cancelled else 'Active'}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=emails,
                fail_silently=True
            )

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        accommodation_id = data.get("accommodation")

        # Ensure the student completed a reservation for this accommodation
        has_reserved = Reservation.objects.filter(
            student=user,
            accommodation_id=accommodation_id,
            status='completed'
        ).exists()

        if not has_reserved:
            raise PermissionDenied("You can only rate accommodations you've completed a reservation for.")

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        rating = serializer.save(student=user)

        # Update average rating
        acc = rating.accommodation
        avg = acc.ratings.aggregate(avg=Avg('value'))['avg'] or 0
        acc.rating = round(avg, 2)
        acc.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
