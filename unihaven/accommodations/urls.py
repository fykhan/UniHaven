from django.urls import path
from .views import (
    accommodation_list_view,
    create_accommodation_view,
    create_reservation_view,
    cancel_reservation_view,
    rate_accommodation_view,
)

urlpatterns = [
    path('', accommodation_list_view, name='accommodation_list'),
    path('add/', create_accommodation_view, name='add_accommodation'),
    path('reserve/', create_reservation_view, name='create_reservation'),
    path('cancel/<int:reservation_id>/', cancel_reservation_view, name='cancel_reservation'),
    path('rate/', rate_accommodation_view, name='rate_accommodation'),
]
