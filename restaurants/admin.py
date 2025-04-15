from django.contrib import admin
from .models import Review, Category, Restaurant, RestaurantReview
# Register your models here.
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(Restaurant)
admin.site.register(RestaurantReview)
