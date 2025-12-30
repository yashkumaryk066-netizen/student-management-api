from django.urls import path
from .views import (
    CarListCreateView,
    CarRetrieveUpdateDestroyView,
    ManufacturerListCreateView,
    ManufacturerRetrieveUpdateDestroyView,
    ServicingCenterListCreateView,
    ServicingCenterRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("cars/", CarListCreateView.as_view()),
    path("cars/<int:id>/", CarRetrieveUpdateDestroyView.as_view()),

    path("manufacturers/", ManufacturerListCreateView.as_view()),
    path("manufacturers/<int:id>/", ManufacturerRetrieveUpdateDestroyView.as_view()),

    path("service-centers/", ServicingCenterListCreateView.as_view()),
    path("service-centers/<int:id>/", ServicingCenterRetrieveUpdateDestroyView.as_view()),
]
