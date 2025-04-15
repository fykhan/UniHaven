from django.urls import path
from .views import (
    student_accommodation_list,
    accommodation_detail,
    create_accommodation_view,
    create_reservation_view,
    cancel_reservation_view,
    rate_accommodation_view,
    view_all_reservations,
    cedars_cancel_reservation,
    my_reservations_view,
    view_all_ratings,
)

urlpatterns = [
    path('', student_accommodation_list, name='accommodation_list'),
    path('<int:pk>/', accommodation_detail, name='accommodation_detail'),
    path('add/', create_accommodation_view, name='create_accommodation'),
    path('reserve/', create_reservation_view, name='create_reservation'),
    path('cancel/<int:pk>/', cancel_reservation_view, name='cancel_reservation'),
    path('rate/', rate_accommodation_view, name='rate_accommodation'),
    path('reservations/', view_all_reservations, name='view_reservations'),
    path('reservations/cancel/<int:pk>/', cedars_cancel_reservation, name='cedars_cancel_reservation'),
    path('my-reservations/', my_reservations_view, name='my_reservations'),
    path('all-ratings/', view_all_ratings, name='view_all_ratings'),
]
