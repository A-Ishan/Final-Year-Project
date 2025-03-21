import requests
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from .models import Review
from django.contrib.auth.decorators import login_required

@login_required
def restaurant_list(request):
    return render(request, 'restaurants/restaurant_list.html') 


def get_nearby_restaurants(request):
    if request.method == "GET":
        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")
        categories = request.GET.getlist("category")  # List of selected categories

        if not latitude or not longitude:
            return JsonResponse({"error": "Location not provided"}, status=400)

        api_key = settings.GOOGLE_PLACES_API_KEY
        base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        params = {
            "location": f"{latitude},{longitude}",
            "radius": 2000,  # 2km radius
            "type": "restaurant",
            "key": api_key
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if "results" in data:
            restaurants = []
            for place in data["results"]:
                name = place.get("name", "Unknown")
                rating = place.get("rating", "N/A")
                address = place.get("vicinity", "No address provided")
                place_id = place.get("place_id")
                image = (
                    f"https://maps.googleapis.com/maps/api/place/photo"
                    f"?maxwidth=400&photoreference={place['photos'][0]['photo_reference']}&key={api_key}"
                    if "photos" in place else None
                )

                if not categories or any(cat.lower() in name.lower() for cat in categories):
                    restaurants.append({
                        "name": name,
                        "rating": rating,
                        "address": address,
                        "image": image,
                        "place_id": place_id
                    })

            return JsonResponse({"restaurants": restaurants})

        return JsonResponse({"error": "No restaurants found"}, status=404)

@login_required
def restaurant_detail(request, place_id):
    reviews = Review.objects.filter(place_id=place_id)
    api_key = settings.GOOGLE_PLACES_API_KEY
    base_url = "https://maps.googleapis.com/maps/api/place/details/json"

    params = {
        "place_id": place_id,
        "fields": "name,rating,formatted_phone_number,website,formatted_address,photos,price_level",
        "key": api_key
    }

    response = requests.get(base_url, params=params)
    data = response.json()
    map_embed_url = f"https://www.google.com/maps/embed/v1/place?q=place_id:{place_id}&key={settings.GOOGLE_PLACES_API_KEY}"
    if request.method == "POST":
        place_id1 = request.POST.get("place_id")
        review_text = request.POST.get("review")
        rating = request.POST.get("rating")
        user = request.user

        if not place_id or not review_text or not rating:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        Review.objects.create(
            place_id=place_id1,
            user=user,
            review_text=review_text,
            rating=rating
        )

    if "result" in data:
        restaurant = {
            "place_id": place_id,
            "name": data["result"].get("name", "Unknown"),
            "rating": data["result"].get("rating", "N/A"),
            "phone": data["result"].get("formatted_phone_number", "No phone number provided"),
            "website": data["result"].get("website", "#"),
            "address": data["result"].get("formatted_address", "No address provided"),
            "price_level": data["result"].get("price_level", "N/A"),
            "image": (
                f"https://maps.googleapis.com/maps/api/place/photo"
                f"?maxwidth=400&photoreference={data['result']['photos'][0]['photo_reference']}&key={api_key}"
                if "photos" in data["result"] else None
            )
        }
        
        return render(request, 'restaurants/restaurants_detail.html', {"restaurant": restaurant, "reviews": reviews, "map_embed_url": map_embed_url})

    return JsonResponse({"error": "Restaurant not found"}, status=404)



   