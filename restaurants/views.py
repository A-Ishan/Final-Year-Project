from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from math import radians, sin, cos, sqrt, atan2
from .models import Review, Category, Restaurant, RestaurantReview
from django.conf import settings

def weighted_average_rating(restaurant):
    # Get all reviews for this restaurant through the intermediate model
    reviews = Review.objects.filter(restaurants=restaurant)
    google_rating = restaurant.google_rating
    
    if not reviews.exists():
        return google_rating

    # Separate reviews by KYC-verified and general users
    kyc_reviews = reviews.filter(user__kyc_verified=True)
    general_reviews = reviews.filter(user__kyc_verified=False)

    # Calculate total ratings and counts
    kyc_total_rating = sum(review.rating for review in kyc_reviews)
    kyc_count = kyc_reviews.count()

    general_total_rating = sum(review.rating for review in general_reviews)
    general_count = general_reviews.count()

    # Handle different cases based on the existence of reviews
    if kyc_count == 0 and general_count == 0:
        return google_rating  # Only Google rating exists
    elif kyc_count == 0:  # No KYC-verified reviews
        combined_rating = (general_total_rating + google_rating) / (general_count + 1)
        return round(combined_rating, 2)
    elif general_count == 0:  # No general user reviews
        combined_rating = (0.6 * (kyc_total_rating / kyc_count)) + (0.4 * google_rating)
        return round(combined_rating, 2)
    else:  # All types of reviews exist
        kyc_weighted = 0.6 * (kyc_total_rating / kyc_count)
        general_weighted = 0.2 * (general_total_rating / general_count)
        google_weighted = 0.2 * google_rating
        combined_rating = kyc_weighted + general_weighted + google_weighted
        return round(combined_rating, 2)

def calculate_distance(user_location, restaurant_location):
    # Radius of the Earth in meters
    EARTH_RADIUS = 6371000

    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = map(radians, user_location)
    lat2, lon2 = map(radians, restaurant_location)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in meters
    distance = EARTH_RADIUS * c
    return round(distance, 2)

@login_required
def restaurant_list(request):
    categories = Category.objects.all()  # Updated class name
    return render(request, 'restaurants/restaurant_list.html', {"categories": categories})

def get_nearby_restaurants(request):
    if request.method == "GET":
        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")
        category_ids = request.GET.getlist("category")  # List of selected category IDs
        keyword = request.GET.get("keyword", "").strip()  # Get search keyword

        if not latitude or not longitude:
            return JsonResponse({"error": "Location not provided"}, status=400)
        
        user_location = [float(latitude), float(longitude)]
        
        # Start with all restaurants
        restaurants_query = Restaurant.objects.all()
        
        # Filter by category if specified
        if category_ids:
            restaurants_query = restaurants_query.filter(categories__id__in=category_ids).distinct()
        
        # Filter by keyword if specified
        if keyword:
            restaurants_query = restaurants_query.filter(name__icontains=keyword)
        
        # Get restaurants within approximately 500m radius
        # This is a rough filter - we'll calculate exact distances next
        max_lat_diff = 0.005  # Approximately 500m in latitude
        max_lon_diff = 0.005  # Approximately 500m in longitude (varies by latitude)
        restaurants_query = restaurants_query.filter(
            latitude__range=(float(latitude) - max_lat_diff, float(latitude) + max_lat_diff),
            longitude__range=(float(longitude) - max_lon_diff, float(longitude) + max_lon_diff)
        )
        
        restaurants_data = []
        locations = []
        
        # Process up to 10 restaurants
        for restaurant in restaurants_query[:10]:
            # Calculate exact distance
            distance = calculate_distance(
                user_location, 
                [restaurant.latitude, restaurant.longitude]
            )
            
            # Skip if beyond 500m (after precise calculation)
            if distance > 500:
                continue
                
            # Calculate weighted rating
            weighted_rating = weighted_average_rating(restaurant)
            
            locations.append({
                'title': restaurant.name, 
                'lat': restaurant.latitude, 
                'lng': restaurant.longitude
            })
            
            restaurants_data.append({
                "name": restaurant.name,
                "rating": weighted_rating,
                "image": restaurant.image,
                "place_id": restaurant.place_id,
                "price_level": restaurant.price_level,
                "distance": distance,
            })

        return JsonResponse({"restaurants": restaurants_data, "locations": locations})
    
    return JsonResponse({"error": "Invalid request method"}, status=400)
    
@login_required
def restaurant_detail(request, place_id):
    restaurant = get_object_or_404(Restaurant, place_id=place_id)
    reviews = Review.objects.filter(restaurants=restaurant)
    
    if request.method == "POST":
        review_text = request.POST.get("review")
        rating = request.POST.get("rating")
        user = request.user

        if not review_text or not rating:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Create the review
        new_review = Review.objects.create(
            place_id=place_id,
            user=user,
            review_text=review_text,
            rating=int(rating)
        )
        
        # Connect the review to the restaurant
        RestaurantReview.objects.create(
            restaurant=restaurant,
            review=new_review
        )

    weighted_rating = weighted_average_rating(restaurant)
    
    # Prepare map embed URL
    map_embed_url = f"https://www.google.com/maps/embed/v1/place?q=place_id:{place_id}&key={settings.GOOGLE_PLACES_API_KEY}"
    
    restaurant_data = {
        "place_id": restaurant.place_id,
        "name": restaurant.name,
        "rating": weighted_rating,
        "address": "",  # You might want to add an address field to your Restaurant model
        "price_level": restaurant.price_level,
        "image": restaurant.image,
    }
    
    return render(request, 'restaurants/restaurants_detail.html', {
        "restaurant": restaurant_data,
        "reviews": reviews,
        "map_embed_url": map_embed_url
    })