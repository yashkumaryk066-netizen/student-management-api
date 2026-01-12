from django.urls import path
from . import views

app_name = 'rangrago'

urlpatterns = [
    path('', views.index, name='index'), # Landing Page / App
    path('api/book/', views.book_ride, name='book_ride'),
    path('api/status/<int:ride_id>/', views.ride_status, name='ride_status'),
]
