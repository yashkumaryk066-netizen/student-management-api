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
from django.views.generic.base import RedirectView
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
    DeveloperProfileView,
    ResumeView,
    service_worker,
    robots_txt,
    sitemap_xml,
    google_verification,
)
from student.ai_chat_views import AIChatView

urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),
    
    # Trigger reload to force update to front-end assets (V5.1)
    # Favicon Fix
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
    path('service-worker.js', service_worker, name='service-worker'),
    
    # SEO
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap_xml),
    path('google7ec15807e3134773.html', google_verification),
    
    # Frontend Pages
    path('', LandingPageView.as_view(), name='landing-page'),
    path('demo/', DemoPageView.as_view(), name='demo-page'),
    path('login/', LoginPageView.as_view(), name='login-page'),
    path('developer/', DeveloperProfileView.as_view(), name='developer-profile-root'),
    path('resume/', ResumeView.as_view(), name='resume-view-root'),
    
    # Dashboard Pages (after login)
    path('dashboard/admin/', AdminDashboardTemplateView.as_view(), name='admin-dashboard'),
    path('dashboard/teacher/', TeacherDashboardTemplateView.as_view(), name='teacher-dashboard'),
    path('dashboard/student/', StudentDashboardTemplateView.as_view(), name='student-dashboard'),
    path('dashboard/parent/', ParentDashboardTemplateView.as_view(), name='parent-dashboard'),
    
    # PWA AI Chat (Direct route, no API prefix)
    path('student/ai-chat/', AIChatView.as_view(), name='pwa-ai-chat-direct'),

    # API Endpoints
    path('api/', include('student.urls')),
    path('api/notifications/', include('notifications.urls')),

    # API Documentation  
    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
]

# Admin Panel Customization
admin.site.site_header = "NextGen ERP Administration"
admin.site.site_title = "NextGen ERP Portal"
admin.site.index_title = "Institute Management Dashboard"
