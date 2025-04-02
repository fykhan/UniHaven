from django.urls import path
from . import views
from .views import home_view, login_view, logout_view, student_selection_view

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('student-selection/', student_selection_view, name='student_selection'),
    path('accommodations/reserve/', views.reserve_view, name='reserve'),  
    path('accommodations/rate/', views.rate_view, name='rate'),  
]
