# create_sample_data.py
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowd_safety.settings')
django.setup()

from monitoring.models import CrowdData

# Clear existing data
CrowdData.objects.all().delete()
print("Cleared old data")

# Create sample data for last 24 hours
locations = [
    {'name': 'Times Square', 'lat': 40.7580, 'lng': -73.9855},
    {'name': 'Shopping Mall', 'lat': 40.7608, 'lng': -73.9845},
    {'name': 'Central Park', 'lat': 40.7829, 'lng': -73.9654},
    {'name': 'Broadway', 'lat': 40.7590, 'lng': -73.9845},
    {'name': 'Union Square', 'lat': 40.7359, 'lng': -73.9911},
]

created_count = 0

for hour in range(24):
    timestamp = datetime.now() - timedelta(hours=hour)
    
    for loc in locations:
        if 10 <= hour <= 17:
            count = random.randint(500, 900)
            density = 'high' if count > 650 else 'medium'
        elif 18 <= hour <= 21:
            count = random.randint(300, 600)
            density = 'medium' if count > 400 else 'low'
        else:
            count = random.randint(20, 150)
            density = 'low'
        
        CrowdData.objects.create(
            location_name=loc['name'],
            latitude=loc['lat'] + random.uniform(-0.005, 0.005),
            longitude=loc['lng'] + random.uniform(-0.005, 0.005),
            density=density,
            count=count,
            timestamp=timestamp
        )
        created_count += 1

print(f"✅ Created {created_count} crowd data points")

# Show summary
high_count = CrowdData.objects.filter(density='high').count()
medium_count = CrowdData.objects.filter(density='medium').count()
low_count = CrowdData.objects.filter(density='low').count()

print(f"\n📊 Data Summary:")
print(f"   🔴 High density: {high_count} points")
print(f"   🟠 Medium density: {medium_count} points")
print(f"   🔵 Low density: {low_count} points")