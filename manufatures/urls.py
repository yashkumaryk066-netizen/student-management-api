"""
URL configuration for manufatures project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from student.views import (
    LandingPageView,
    LoginPageView,
    DemoPageView,
    AdminDashboardTemplateView,
    TeacherDashboardTemplateView,
    StudentDashboardTemplateView,
    ParentDashboardTemplateView,
)

urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),
    
    # Trigger reload to force update to front-end assets (V5.1)
    # Frontend Pages
    path('', LandingPageView.as_view(), name='landing-page'),
    path('demo/', DemoPageView.as_view(), name='demo-page'),
    path('login/', LoginPageView.as_view(), name='login-page'),
    
    # Dashboard Pages (after login)
    path('dashboard/admin/', AdminDashboardTemplateView.as_view(), name='admin-dashboard'),
    path('dashboard/teacher/', TeacherDashboardTemplateView.as_view(), name='teacher-dashboard'),
    path('dashboard/student/', StudentDashboardTemplateView.as_view(), name='student-dashboard'),
    path('dashboard/parent/', ParentDashboardTemplateView.as_view(), name='parent-dashboard'),

    # API Endpoints
    path('api/', include('student.urls')),

    # API Documentation  
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
]

# Admin Panel Customization
admin.site.site_header = "NextGen ERP Administration"
admin.site.site_title = "NextGen ERP Portal"
admin.site.index_title = "Institute Management Dashboard"
