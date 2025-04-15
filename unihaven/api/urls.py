from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    AccommodationViewSet,
    ReservationViewSet,
    RatingViewSet,
)
from .views import AddressLookupView, AccommodationFilterView  

router = DefaultRouter()
router.register(r'accommodations', AccommodationViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path("accommodations/filter/", AccommodationFilterView.as_view(), name="accommodation-filter"),
    path('address-lookup/', AddressLookupView.as_view(), name='address-lookup'),
    path('', include(router.urls)),
]