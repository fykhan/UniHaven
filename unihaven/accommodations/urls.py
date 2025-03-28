from django.urls import path
from .views import (
    AccommodationList, CreateReservation, CancelReservation,
    CreateAccommodation, RateAccommodation
)

urlpatterns = [
    path('accommodations/', AccommodationList.as_view(), name='accommodation-list'),
    path('accommodations/add/', CreateAccommodation.as_view(), name='create-accommodation'),
    path('reservations/', CreateReservation.as_view(), name='create-reservation'),
    path('reservations/cancel/<int:reservation_id>/', CancelReservation.as_view(), name='cancel-reservation'),
    path('accommodations/rate/', RateAccommodation.as_view(), name='rate-accommodation'),
]
