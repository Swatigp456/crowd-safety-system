# alerts/services.py
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Alert, AlertRecipient
from accounts.models import User
import logging

logger = logging.getLogger(__name__)

class GlobalAlertService:
    """Service to fetch real-time alerts from global APIs"""
    
    def __init__(self):
        self.api_sources = {
            'earthquake': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson',
            'weather': 'https://api.weather.gov/alerts/active',
            'disasters': 'https://www.gdacs.org/xml/rss.xml',
        }
        
    def fetch_earthquake_alerts(self):
        """Fetch real-time earthquake alerts from USGS"""
        try:
            response = requests.get(self.api_sources['earthquake'], timeout=10)
            if response.status_code == 200:
                data = response.json()
                alerts = []
                
                for feature in data.get('features', [])[:10]:
                    props = feature['properties']
                    coords = feature['geometry']['coordinates']
                    
                    magnitude = props.get('mag', 0)
                    place = props.get('place', 'Unknown location')
                    time_ms = props.get('time', 0)
                    
                    if magnitude >= 2.5:
                        if magnitude >= 6.0:
                            priority = 'emergency'
                        elif magnitude >= 5.0:
                            priority = 'high'
                        elif magnitude >= 4.0:
                            priority = 'medium'
                        else:
                            priority = 'low'
                        
                        alert = {
                            'title': f"🌍 Earthquake: M{magnitude} - {place}",
                            'message': f"Magnitude {magnitude} earthquake detected at {place}. Time: {datetime.fromtimestamp(time_ms/1000).strftime('%Y-%m-%d %H:%M:%S')} UTC.",
                            'alert_type': 'natural_disaster',
                            'priority': priority,
                            'location': place,
                            'latitude': coords[1] if len(coords) > 1 else 0,
                            'longitude': coords[0] if len(coords) > 0 else 0,
                            'source': 'USGS',
                            'external_id': props.get('id', ''),
                            'magnitude': magnitude
                        }
                        alerts.append(alert)
                return alerts
        except Exception as e:
            logger.error(f"Error fetching earthquake alerts: {e}")
            return []
    
    def fetch_weather_alerts(self):
        """Fetch real-time weather alerts"""
        try:
            response = requests.get(self.api_sources['weather'], timeout=10)
            if response.status_code == 200:
                data = response.json()
                alerts = []
                
                for feature in data.get('features', [])[:10]:
                    props = feature.get('properties', {})
                    
                    severity = props.get('severity', 'Unknown')
                    urgency = props.get('urgency', 'Unknown')
                    headline = props.get('headline', 'Weather Alert')
                    description = props.get('description', '')
                    area = props.get('areaDesc', 'Unknown area')
                    
                    if severity == 'Extreme' or urgency == 'Immediate':
                        priority = 'emergency'
                    elif severity == 'Severe':
                        priority = 'high'
                    elif severity == 'Moderate':
                        priority = 'medium'
                    else:
                        priority = 'low'
                    
                    alert = {
                        'title': f"⚠️ Weather: {headline[:100]}",
                        'message': f"{description[:500]}",
                        'alert_type': 'weather',
                        'priority': priority,
                        'location': area,
                        'source': 'NOAA',
                        'external_id': props.get('id', '')
                    }
                    alerts.append(alert)
                return alerts
        except Exception as e:
            logger.error(f"Error fetching weather alerts: {e}")
            return []
    
    def fetch_disaster_alerts(self):
        """Fetch disaster alerts from GDACS"""
        try:
            response = requests.get(self.api_sources['disasters'], timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                alerts = []
                
                for item in root.findall('.//item')[:10]:
                    title_elem = item.find('title')
                    title = title_elem.text if title_elem is not None else ''
                    desc_elem = item.find('description')
                    description = desc_elem.text if desc_elem is not None else ''
                    
                    alert = {
                        'title': f"🚨 Disaster: {title[:100]}",
                        'message': description[:500] if description else title,
                        'alert_type': 'natural_disaster',
                        'priority': 'high',
                        'location': 'Global',
                        'source': 'GDACS',
                        'external_id': datetime.now().strftime('%Y%m%d%H%M%S')
                    }
                    alerts.append(alert)
                return alerts
        except Exception as e:
            logger.error(f"Error fetching disaster alerts: {e}")
            return []

class RealTimeAlertManager:
    def __init__(self):
        self.service = GlobalAlertService()
    
    def get_all_global_alerts(self):
        all_alerts = []
        all_alerts.extend(self.service.fetch_earthquake_alerts())
        all_alerts.extend(self.service.fetch_weather_alerts())
        all_alerts.extend(self.service.fetch_disaster_alerts())
        
        priority_order = {'emergency': 4, 'high': 3, 'medium': 2, 'low': 1}
        all_alerts.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 0), reverse=True)
        return all_alerts
    
    def process_and_save_alerts(self):
        alerts = self.get_all_global_alerts()
        saved_count = 0
        
        for alert_data in alerts:
            existing = Alert.objects.filter(
                title=alert_data['title'],
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).exists()
            
            if not existing:
                try:
                    alert = Alert.objects.create(
                        title=alert_data['title'],
                        message=alert_data['message'],
                        alert_type=alert_data.get('alert_type', 'natural_disaster'),
                        priority=alert_data.get('priority', 'medium'),
                        location=alert_data.get('location', 'Global'),
                        latitude=alert_data.get('latitude'),
                        longitude=alert_data.get('longitude'),
                        created_by=None,
                        is_active=True,
                        source=alert_data.get('source', 'Global Alert System'),
                        external_id=alert_data.get('external_id', '')
                    )
                    
                    recipients = User.objects.filter(is_active=True)
                    for recipient in recipients:
                        AlertRecipient.objects.create(
                            alert=alert,
                            user=recipient,
                            sent_via_app=True
                        )
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Error saving alert: {e}")
        return saved_count