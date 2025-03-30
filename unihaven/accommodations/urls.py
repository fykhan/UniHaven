from django.urls import path
from .views import (
    AccommodationList,
    CreateAccommodation,
    CreateReservation,
    CancelReservation,
    RateAccommodation,
)

urlpatterns = [
    path('list/', AccommodationList.as_view(), name='accommodation_list'),
    path('add/', CreateAccommodation.as_view(), name='add_accommodation'),
    path('reserve/', CreateReservation.as_view(), name='create_reservation'),
    path('cancel/<int:reservation_id>/', CancelReservation.as_view(), name='cancel_reservation'),
    path('rate/', RateAccommodation.as_view(), name='rate_accommodation'),
]
