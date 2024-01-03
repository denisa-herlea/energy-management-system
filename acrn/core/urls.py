from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('measurements', views.MeasurementViewset, basename='measurements')

urlpatterns = [
    path('', include(router.urls)),
]
