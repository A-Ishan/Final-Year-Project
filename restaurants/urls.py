from django.urls import path
from .views import scan_nearby_restaurants

urlpatterns = [
    path("scan/", scan_nearby_restaurants, name="scan"),
]