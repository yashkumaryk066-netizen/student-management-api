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
    # Frontend Pages
    path('', LandingPageView.as_view(), name='landing-page'),
    path('demo/', DemoPageView.as_view(), name='demo-page'),
    path('login.html', LoginPageView.as_view(), name='login-page'),
    path('dashboard/admin.html', AdminDashboardTemplateView.as_view(), name='admin-dashboard-page'),
    path('dashboard/teacher.html', TeacherDashboardTemplateView.as_view(), name='teacher-dashboard-page'),
    path('dashboard/student.html', StudentDashboardTemplateView.as_view(), name='student-dashboard-page'),
    path('dashboard/parent.html', ParentDashboardTemplateView.as_view(), name='parent-dashboard-page'),

    # API
    path('api/', include('student.urls')),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
]
