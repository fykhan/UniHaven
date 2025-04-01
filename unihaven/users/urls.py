from django.urls import path
from . import views
from .views import student_selection_view

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('student_selection/', student_selection_view, name='student_selection'), 
]
