from django.urls import path
from .views import (
    StudentListCreateView,
    StudentDetailsView,
    StudentTodayView,
    AttendenceCreateView,
    AttendenceDetailsView,
    ProfileView
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [

    #STUDENT
    path("students/", StudentListCreateView.as_view(), name="student-list-create"),
    path("students/<int:id>/", StudentDetailsView.as_view(), name="student-detail"),
    path("students/today/", StudentTodayView.as_view(), name="student-today"),
    #ATTENDENCE
    path("attendence/", AttendenceCreateView.as_view(), name="attendence-list-create"),
    path("attendence/<int:id>/", AttendenceDetailsView.as_view(), name="attendence-detail"),
    #AUTH (JWT)
    path("auth/login/", TokenObtainPairView.as_view(), name="jwt-login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    #PROFILE
    path("profile/", ProfileView.as_view(), name="profile"),
]
