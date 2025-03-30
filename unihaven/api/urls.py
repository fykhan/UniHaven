from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccommodationViewSet,
    ReservationViewSet,
    RatingViewSet,
    AddressLookupView
)

router = DefaultRouter()
router.register(r'accommodations', AccommodationViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('address-lookup/', AddressLookupView.as_view(), name='address-lookup'),
]
