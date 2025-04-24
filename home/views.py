import requests
from django.conf import settings
from restaurants.models import Restaurant
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def home(request):
    API_KEY = settings.GOOGLE_PLACES_API_KEY
    LOCATION = "27.7172,85.3240"  
    RADIUS = 5000  
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


def about(request):
    return render(request, 'home/about.html')



def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact_us')
    else:
        form = ContactForm()
    return render(request, 'home/contacts.html', {'form': form})
