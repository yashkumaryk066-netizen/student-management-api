from django.urls import path
from . import views

app_name = 'rangrago'

urlpatterns = [
    # Rider App
    path('', views.index, name='index'), 
    path('login/', views.rider_login, name='rider_login'),
    
    # Driver App
    path('drive/', views.driver_login, name='driver_login'),
    path('drive/dashboard/', views.driver_dashboard, name='driver_dashboard'),
    
    # APIs (Rider)
    path('api/book/', views.book_ride, name='book_ride'),
    path('api/status/<int:ride_id>/', views.ride_status, name='ride_status'),
    
    # APIs (Driver)
    path('api/driver/toggle/', views.toggle_driver_status, name='toggle_driver_status'),
    path('api/driver/poll/', views.fetch_available_rides, name='fetch_available_rides'),
    path('api/driver/accept/<int:ride_id>/', views.accept_ride, name='accept_ride'),
]
