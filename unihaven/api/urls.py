from django.urls import path, include
from .views import HealthCheck

urlpatterns = [
    path('health/', HealthCheck.as_view(), name='health-check'),
    path('users/', include('users.urls')),
    path('accommodation/', include('accommodation.urls')),
]
