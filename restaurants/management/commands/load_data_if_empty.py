import csv
import os
import ast

from django.core.management.base import BaseCommand
from django.conf import settings
from restaurants.models import Restaurant, Category  # Change to your actual app name

class Command(BaseCommand):
    help = "Load restaurants and categories from CSV if tables are empty"

    def handle(self, *args, **kwargs):
        # Replace this with your actual Google Places API Key
        GOOGLE_API_KEY = settings.GOOGLE_PLACES_API_KEY

        if Restaurant.objects.exists() or Category.objects.exists():
            self.stdout.write(self.style.WARNING("Tables already contain data. Aborting."))
            return

        file_path = os.path.join(settings.BASE_DIR, 'dataset.csv')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"CSV file not found at {file_path}"))
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                try:
                    # Parse geometry to extract lat/lng
                    geometry = ast.literal_eval(row['geometry'])
                    latitude = geometry['location']['lat']
                    longitude = geometry['location']['lng']

                    # Parse categories from 'types'
                    type_string = row.get('types', '')
                    category_names = [c.strip() for c in type_string.strip("[]").replace("'", "").split(',') if c.strip()]
                    category_objs = []
                    for name in category_names:
                        category_obj, _ = Category.objects.get_or_create(name=name)
                        category_objs.append(category_obj)

                    # Generate Google Places image URL
                    photo_url = ''
                    photos_raw = row.get('photos', '')
                    if photos_raw:
                        try:
                            photo_list = ast.literal_eval(photos_raw)
                            if isinstance(photo_list, list) and photo_list:
                                photo_ref = photo_list[0].get('photo_reference')
                                max_width = photo_list[0].get('width', 400)  # default width
                                if photo_ref:
                                    photo_url = (
                                        f"https://maps.googleapis.com/maps/api/place/photo"
                                        f"?maxwidth={max_width}&photo_reference={photo_ref}&key={GOOGLE_API_KEY}"
                                    )
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"⚠️ Error parsing photo: {e}"))

                    # Create restaurant
                    restaurant = Restaurant.objects.create(
                        place_id=row['place_id'],
                        name=row['name'],
                        latitude=latitude,
                        longitude=longitude,
                        image=photo_url,
                        price_level=row.get('price_level', '') or '',
                        google_rating=float(row['rating']) if row.get('rating') not in [None, ''] else 0.0,
                        number_of_reviews=int(float(row['user_ratings_total'])) if row.get('user_ratings_total') not in [None, ''] else 0,
                    )
                    restaurant.categories.set(category_objs)

                    self.stdout.write(self.style.SUCCESS(f"✅ Added: {restaurant.name}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Failed to process row: {row.get('name', 'Unknown')} — {e}"))

        self.stdout.write(self.style.SUCCESS("🎉 Data loading complete."))
