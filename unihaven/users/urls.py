from django.urls import path
from .views import (
    home_view,
    login_view,
    logout_view,
    student_selection_view,
    cedars_dashboard_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('student_selection/', student_selection_view, name='student_selection'),
    path('cedars-dashboard/', cedars_dashboard_view, name='cedars_dashboard'),
]
