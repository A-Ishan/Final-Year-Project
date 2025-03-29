from django.shortcuts import render
import requests
from django.conf import settings

def home(request):
    API_KEY = settings.GOOGLE_PLACES_API_KEY
    LOCATION = "27.7172,85.3240"  # Latitude and Longitude for Kathmandu
    RADIUS = 5000  # Search radius in meters
    TYPE = "restaurant"

    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    url += f"location={LOCATION}&radius={RADIUS}&type={TYPE}&key={API_KEY}&rankby=prominence"

    response = requests.get(url)
    data = response.json()

    restaurants = []
    if "results" in data:
        restaurants = [
            {
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating", "N/A"),
                "user_ratings_total": place.get("user_ratings_total", 0),
                "photo": place["photos"][0]["photo_reference"] if "photos" in place else None,
                "place_id": place["place_id"],
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"],
            }
            for place in data["results"][:6]  # Fetching the top 6 for display
        ]

    return render(request, 'home/home.html', {'restaurants': restaurants, 'api_key': API_KEY})