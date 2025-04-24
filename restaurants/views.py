import math
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Avg

from .models import Review, Category, Restaurant, RestaurantReview


def distance_approx(lat1, lon1, lat2, lon2):
    dx = 111000 * math.cos(math.radians((lat1 + lat2) / 2)) * (lon2 - lon1)
    dy = 111000 * (lat2 - lat1)
    return math.sqrt(dx * dx + dy * dy)


def calculate_simple_rating(restaurant):
    reviews = Review.objects.filter(
        id__in=RestaurantReview.objects.filter(restaurant=restaurant).values_list('review_id', flat=True)
    )

    verified_reviews = reviews.filter(user__kyc_verified=True)
    general_reviews = reviews.filter(user__kyc_verified=False)

    verified_avg = verified_reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    general_avg = general_reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    review_count = reviews.count() + restaurant.number_of_reviews

    if review_count == 0:
        return round(restaurant.google_rating or 3.5, 1), review_count

    if verified_reviews.exists() and general_reviews.exists():
        rating = (0.7 * verified_avg) + (0.3 * general_avg)
    elif verified_reviews.exists():
        rating = verified_avg
    elif general_reviews.exists():
        rating = general_avg
    else:
        rating = restaurant.google_rating or 3.5

    rating = min(rating + min(review_count / 100, 0.5), 5.0)

    return round(rating, 1), review_count


@login_required
def restaurant_list(request):
    categories = Category.objects.all()
    return render(request, 'restaurants/restaurant_list.html', {
        "categories": categories,
        "api_key": settings.GOOGLE_PLACES_API_KEY
    })


def get_nearby_restaurants(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        user_lat = float(request.GET.get("latitude", 0))
        user_lng = float(request.GET.get("longitude", 0))
        category_id = request.GET.get("category", "").strip()
        keyword = request.GET.get("keyword", "").strip()
        mode = request.GET.get("mode", "top")

        restaurants = Restaurant.objects.all()

        if category_id and category_id.isdigit():
            restaurants = restaurants.filter(categories__id=int(category_id))

        if keyword:
            restaurants = restaurants.filter(name__icontains=keyword)

        results = []
        for r in restaurants:
            dist = distance_approx(user_lat, user_lng, r.latitude, r.longitude)
            rating, review_count = calculate_simple_rating(r)

            if mode == "nearby" and dist > 500:
                continue

            results.append({
                "restaurant": r,
                "distance": dist,
                "rating": rating,
                "review_count": review_count
            })

        if mode == "nearby":
            results.sort(key=lambda x: x["distance"])
        else:
            results.sort(key=lambda x: (-x["rating"], x["distance"]))

        top_results = results[:10]

        restaurants_data = [{
            "id": item["restaurant"].id,
            "name": item["restaurant"].name,
            "rating": item["rating"],
            "image": item["restaurant"].image,
            "place_id": item["restaurant"].place_id,
            "price_level": item["restaurant"].price_level,
            "distance": round(item["distance"], 2),
            "review_count": item["review_count"],
        } for item in top_results]

        locations = [{
            "title": item["restaurant"].name,
            "lat": item["restaurant"].latitude,
            "lng": item["restaurant"].longitude
        } for item in top_results]

        return JsonResponse({"restaurants": restaurants_data, "locations": locations})

    except (ValueError, TypeError) as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def restaurant_detail(request, place_id):
    restaurant = get_object_or_404(Restaurant, place_id=place_id)

    reviews = Review.objects.filter(
        id__in=RestaurantReview.objects.filter(restaurant=restaurant).values_list('review_id', flat=True)
    )

    if request.method == "POST":
        review_text = request.POST.get("review")
        rating = request.POST.get("rating")

        if review_text and rating:
            new_review = Review.objects.create(
                place_id=place_id,
                user=request.user,
                review_text=review_text,
                rating=int(rating)
            )
            RestaurantReview.objects.create(restaurant=restaurant, review=new_review)

    rating, _ = calculate_simple_rating(restaurant)

    return render(request, 'restaurants/restaurants_detail.html', {
        "restaurant": {
            "place_id": restaurant.place_id,
            "name": restaurant.name,
            "rating": rating,
            "price_level": restaurant.price_level,
            "image": restaurant.image,
        },
        "reviews": reviews,
        "map_embed_url": f"https://www.google.com/maps/embed/v1/place?q=place_id:{place_id}&key={settings.GOOGLE_PLACES_API_KEY}"
    })
