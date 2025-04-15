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
    
    class Meta:
        indexes = [
            models.Index(fields=['place_id']),
            models.Index(fields=['user']),
        ]
    
class Category(models.Model):  
    
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories" 
    
class Restaurant(models.Model):
    
    place_id = models.CharField(max_length=255, unique=True)  
    name = models.CharField(max_length=255)  
    latitude = models.FloatField()  
    longitude = models.FloatField()  
    image = models.URLField()  
    price_level = models.CharField(max_length=50) 
    google_rating = models.FloatField()  
    number_of_reviews = models.PositiveIntegerField() 
    categories = models.ManyToManyField(Category, blank=True) 
    
    def __str__(self):
        return self.name
    
    class Meta:
        indexes = [
            models.Index(fields=['place_id']),
            models.Index(fields=['name']),
        ]

class RestaurantReview(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.restaurant.name} review by {self.review.user}"
    
    class Meta:
        unique_together = ['restaurant', 'review'] 