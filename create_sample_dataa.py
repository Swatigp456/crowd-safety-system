# create_sample_data.py
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowd_safety.settings')
django.setup()

from monitoring.models import CrowdData
from incidents.models import Incident
from accounts.models import User

print("Creating sample data for ML training...")

# Get or create admin user
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()

# Create sample crowd data (200 points)
print("Creating crowd data...")
for i in range(200):
    hour = random.randint(0, 23)
    if 10 <= hour <= 17:
        count = random.randint(400, 900)
        density = 'high' if count > 650 else 'medium'
    elif 18 <= hour <= 21:
        count = random.randint(200, 500)
        density = 'medium' if count > 300 else 'low'
    else:
        count = random.randint(20, 150)
        density = 'low'
    
    CrowdData.objects.create(
        location_name=random.choice(['Times Square', 'Central Park', 'Shopping Mall', 'Broadway', 'Union Square']),
        latitude=40.7128 + random.uniform(-0.05, 0.05),
        longitude=-74.0060 + random.uniform(-0.05, 0.05),
        density=density,
        count=count,
        timestamp=datetime.now() - timedelta(hours=random.randint(0, 168))
    )

print(f"✅ Created {CrowdData.objects.count()} crowd data points")

# Create sample incidents (50 points)
print("Creating incident data...")
incident_types = ['accident', 'medical', 'security', 'crowd', 'fire', 'other']
titles = {
    'accident': ['Car accident', 'Vehicle collision', 'Road accident', 'Car crash', 'Bike accident'],
    'medical': ['Medical emergency', 'Person fainted', 'Heart attack', 'Injury reported', 'Medical help needed'],
    'security': ['Fight reported', 'Security threat', 'Suspicious person', 'Theft reported', 'Vandalism'],
    'crowd': ['Overcrowding', 'Stampede risk', 'Crowd surge', 'Too many people', 'Crowd control needed'],
    'fire': ['Fire reported', 'Smoke detected', 'Building fire', 'Vehicle fire', 'Fire alarm'],
    'other': ['Suspicious activity', 'Noise complaint', 'Lost child', 'Animal on road', 'Water leakage']
}

descriptions = {
    'accident': ['Two vehicles collided', 'Car hit the barrier', 'Multiple vehicles involved', 'Driver lost control', 'Accident causing traffic'],
    'medical': ['Person needs immediate medical attention', 'Someone collapsed', 'Medical assistance required', 'Person injured', 'Emergency medical situation'],
    'security': ['Security personnel needed', 'Disturbance reported', 'Unauthorized access', 'Suspicious behavior', 'Security incident'],
    'crowd': ['Large crowd forming', 'Dangerous crowding', 'People pushing', 'Overcapacity situation', 'Crowd management needed'],
    'fire': ['Fire visible', 'Smoke coming out', 'Fire department needed', 'Burning smell', 'Flames reported'],
    'other': ['Unusual activity', 'Need assistance', 'Reported incident', 'Situation developing', 'Check required']
}

for i in range(50):
    incident_type = random.choice(incident_types)
    title = random.choice(titles.get(incident_type, titles['other']))
    description = random.choice(descriptions.get(incident_type, descriptions['other']))
    
    Incident.objects.create(
        title=title,
        description=description,
        incident_type=incident_type,
        status=random.choice(['pending', 'investigating', 'resolved']),
        location=random.choice(['Times Square', 'Central Park', 'Shopping Mall', 'Broadway', 'Union Square']),
        latitude=40.7128 + random.uniform(-0.05, 0.05),
        longitude=-74.0060 + random.uniform(-0.05, 0.05),
        reported_by=admin_user,
        reported_at=datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
    )

print(f"✅ Created {Incident.objects.count()} incident data points")

print("\n" + "="*50)
print("✅ Sample data created successfully!")
print("="*50)
print("\nNow you can train the ML models from the ML Dashboard:")
print("1. Go to: http://127.0.0.1:8000/ml/")
print("2. Click 'Train Crowd Model'")
print("3. Click 'Train Incident Model'")
print("4. Click 'Train Anomaly Model'")