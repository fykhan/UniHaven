from django.urls import path
from .views import (
    student_accommodation_list,
    accommodation_detail,
    create_accommodation_view,
    create_reservation_view,
    cancel_reservation_view,
    rate_accommodation_view,
    view_all_reservations,
    cedars_cancel_reservation
)

urlpatterns = [
    # Student
    path('', student_accommodation_list, name='student_accommodations'),
    path('<int:pk>/', accommodation_detail, name='accommodation_detail'),
    path('reserve/', create_reservation_view, name='create_reservation'),
    path('cancel/<int:pk>/', cancel_reservation_view, name='cancel_reservation'),
    path('rate/', rate_accommodation_view, name='rate_accommodation'),

    # CEDARS
    path('add/', create_accommodation_view, name='add_accommodation'),
    path('reservations/', view_all_reservations, name='view_reservations'),
    path('cancel-admin/<int:pk>/', cedars_cancel_reservation, name='cedars_cancel_reservation'),
]
