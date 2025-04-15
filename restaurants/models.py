from django.conf import settings
from django.db import models

class Review(models.Model):
    place_id = models.CharField(max_length=255)  
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    review_text = models.TextField()  
    rating = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True) 
 
    def __str__(self):
        return f"Review by {self.user} for place_id {self.place_id}"
    
class catagory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    
class Restaurant(models.Model):
    id = models.AutoField(primary_key=True)
    place_id = models.CharField(max_length=255, unique=True)  
    name = models.CharField(max_length=255)  
    latitude = models.FloatField()  
    longitude = models.FloatField()  
    image = models.URLField()  
    price_level = models.CharField(max_length=50) 
    google_rating = models.FloatField()  
    number_of_reviews = models.PositiveIntegerField() 
    catagory_list = models.ManyToManyField(catagory, blank=True) 
    reviews = models.ManyToManyField(Review, blank=True, related_name='restaurants', through='RestaurantReview')

class RestaurantReview(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)


