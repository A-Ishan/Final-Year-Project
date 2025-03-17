from django.conf import settings
from django.db import models

class Review(models.Model):
    place_id = models.CharField(max_length=255)  
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to custom user model
    review_text = models.TextField()  # The actual review text
    rating = models.PositiveIntegerField()  # Rating (e.g., 1-5)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the creation time of the review
 
    def __str__(self):
        return f"Review by {self.user} for place_id {self.place_id}"