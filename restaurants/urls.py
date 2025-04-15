from django.urls import path
from .views import restaurant_list, get_nearby_restaurants, restaurant_detail

urlpatterns = [
    path('', restaurant_list, name='restaurants'),
    path('get_nearby_restaurants/', get_nearby_restaurants, name='get_nearby_restaurants'),
    path('<str:place_id>/', restaurant_detail, name='restaurant_detail'),
    
]
