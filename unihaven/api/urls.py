from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.viewsets import AccommodationViewSet, ReservationViewSet, RatingViewSet
from api.views import AccommodationFilterView, ReservationFilterView, ReservationCancelView, MeView

router = DefaultRouter()
router.register(r'accommodations', AccommodationViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path("accommodations/filter/", AccommodationFilterView.as_view(), name="accommodation-filter"),
    path("reservations/filter/", ReservationFilterView.as_view(), name="reservation-filter"),
    path("reservations/<int:pk>/cancel/", ReservationCancelView.as_view(), name="reservation-cancel"),
    path("me/", MeView.as_view(), name="me-view"),
    path('', include(router.urls)),
]
