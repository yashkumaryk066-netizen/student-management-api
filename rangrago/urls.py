from django.urls import path
from . import views

app_name = 'rangrago'

urlpatterns = [
    # Rider App
    path('', views.index, name='index'), 
    
    # Driver App
    path('drive/', views.driver_login, name='driver_login'),
    path('drive/dashboard/', views.driver_dashboard, name='driver_dashboard'),
    
    # APIs
    path('api/book/', views.book_ride, name='book_ride'),
    path('api/status/<int:ride_id>/', views.ride_status, name='ride_status'),
]
