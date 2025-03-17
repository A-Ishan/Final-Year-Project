from django.shortcuts import render
from django.shortcuts import render
from django.conf import settings

GOOGLE_PLACES_API_KEY=settings.GOOGLE_PLACES_API_KEY
def scan_nearby_restaurants(request):
    """Fetch nearby restaurants using Google Places API."""
    latitude = request.GET.get("lat", "27.7172")  # Default: Kathmandu
    longitude = request.GET.get("lng", "85.3240")  # Default: Kathmandu
    radius = 1000  # 5km radius

    # Google Places API URL
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius={radius}&type=restaurant&key={GOOGLE_PLACES_API_KEY}"

    # Make the request
    response = requests.get(url)
    data = response.json()

    # Process data
    restaurants = []
    for place in data.get("results", []):
        restaurants.append({
            "name": place.get("name", "Unknown Restaurant"),
            "rating": place.get("rating", "N/A"),
            "address": place.get("vicinity", "No address available"),
            "place_id": place.get("place_id"),
            "photo": (
                f"https://maps.googleapis.com/maps/api/place/photo"
                f"?maxwidth=400&photoreference={place['photos'][0]['photo_reference']}&key={GOOGLE_PLACES_API_KEY}"
                if "photos" in place else "https://bitsofco.de/img/Qo5mfYDE5v-350.png"
            ),
        })

    return render(request, "restaurants/scan.html", {"restaurants": restaurants})