# ml/services.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
from django.conf import settings
import pickle
from datetime import datetime, timedelta
from django.utils import timezone
import logging
import json

logger = logging.getLogger(__name__)

class CrowdMLService:
    """Machine Learning Service for Crowd Safety System"""
    
    def __init__(self):
        self.model_path = os.path.join(settings.BASE_DIR, 'ml/models/')
        self.ensure_model_directory()
        self.load_models()
    
    def ensure_model_directory(self):
        """Create model directory if not exists"""
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
    
    def load_models(self):
        """Load pre-trained models"""
        self.crowd_predictor = None
        self.incident_classifier = None
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        
        # Load models if they exist
        try:
            if os.path.exists(os.path.join(self.model_path, 'crowd_predictor.pkl')):
                self.crowd_predictor = joblib.load(os.path.join(self.model_path, 'crowd_predictor.pkl'))
            if os.path.exists(os.path.join(self.model_path, 'incident_classifier.pkl')):
                self.incident_classifier = joblib.load(os.path.join(self.model_path, 'incident_classifier.pkl'))
            if os.path.exists(os.path.join(self.model_path, 'anomaly_detector.pkl')):
                self.anomaly_detector = joblib.load(os.path.join(self.model_path, 'anomaly_detector.pkl'))
            if os.path.exists(os.path.join(self.model_path, 'scaler.pkl')):
                self.scaler = joblib.load(os.path.join(self.model_path, 'scaler.pkl'))
            logger.info("ML models loaded successfully")
        except Exception as e:
            logger.info(f"Error loading models: {e}")
    
    def train_crowd_predictor(self, historical_data):
        """Train model to predict crowd density"""
        if len(historical_data) < 20:
            return {"status": "error", "message": f"Insufficient data for training (need at least 20 samples, have {len(historical_data)})"}
        
        try:
            # Prepare features
            df = pd.DataFrame(historical_data)
            
            # Extract features
            features = []
            labels = []
            
            for _, row in df.iterrows():
                hour = row.get('hour', 0)
                day = row.get('day_of_week', 0)
                location = hash(row.get('location', '')) % 100
                previous_crowd = row.get('previous_crowd', 0)
                
                features.append([hour, day, location, previous_crowd])
                labels.append(row.get('crowd_level', 1))
            
            if len(features) < 10:
                return {"status": "error", "message": "Not enough valid data points"}
            
            # Train model
            self.crowd_predictor = RandomForestClassifier(n_estimators=50, random_state=42)
            self.crowd_predictor.fit(features, labels)
            
            # Save model
            joblib.dump(self.crowd_predictor, os.path.join(self.model_path, 'crowd_predictor.pkl'))
            
            return {
                "status": "success",
                "message": f"Crowd predictor trained with {len(features)} samples"
            }
            
        except Exception as e:
            logger.error(f"Error training crowd predictor: {e}")
            return {"status": "error", "message": str(e)}
    
    def train_incident_classifier(self, historical_incidents):
        """Train model to classify incident types"""
        if len(historical_incidents) < 10:
            return {"status": "error", "message": f"Insufficient data for training (need at least 10 incidents, have {len(historical_incidents)})"}
        
        try:
            df = pd.DataFrame(historical_incidents)
            
            # Extract features from text
            features = []
            labels = []
            
            for _, row in df.iterrows():
                text = (str(row.get('title', '')) + " " + str(row.get('description', ''))).lower()
                
                # Simple text features
                word_count = len(text.split())
                char_count = len(text)
                has_emergency_words = int(any(word in text for word in ['fire', 'accident', 'emergency', 'help', 'urgent']))
                has_location_words = int(any(word in text for word in ['road', 'street', 'area', 'building', 'place']))
                
                features.append([word_count, char_count, has_emergency_words, has_location_words, row.get('hour', 12)])
                labels.append(row.get('incident_type', 'other'))
            
            if len(features) < 5:
                return {"status": "error", "message": "Not enough valid data points"}
            
            # Train model
            self.incident_classifier = RandomForestClassifier(n_estimators=50, random_state=42)
            self.incident_classifier.fit(features, labels)
            
            # Save model
            joblib.dump(self.incident_classifier, os.path.join(self.model_path, 'incident_classifier.pkl'))
            
            return {
                "status": "success",
                "message": f"Incident classifier trained with {len(features)} samples"
            }
            
        except Exception as e:
            logger.error(f"Error training incident classifier: {e}")
            return {"status": "error", "message": str(e)}
    
    def train_anomaly_detector(self, normal_data):
        """Train anomaly detection model"""
        if len(normal_data) < 10:
            return {"status": "error", "message": f"Insufficient data for training (need at least 10 samples, have {len(normal_data)})"}
        
        try:
            # Prepare features
            features = []
            for item in normal_data:
                features.append([
                    float(item.get('crowd_count', 0)),
                    int(item.get('hour', 0)),
                    int(item.get('day_of_week', 0))
                ])
            
            if len(features) < 5:
                return {"status": "error", "message": "Not enough valid data points"}
            
            # Train isolation forest
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            self.anomaly_detector.fit(features)
            
            # Train scaler
            self.scaler.fit(features)
            
            # Save models
            joblib.dump(self.anomaly_detector, os.path.join(self.model_path, 'anomaly_detector.pkl'))
            joblib.dump(self.scaler, os.path.join(self.model_path, 'scaler.pkl'))
            
            return {
                "status": "success",
                "message": f"Anomaly detector trained with {len(features)} samples"
            }
            
        except Exception as e:
            logger.error(f"Error training anomaly detector: {e}")
            return {"status": "error", "message": str(e)}
    
    def predict_crowd_density(self, hour, day_of_week, location, previous_crowd):
        """Predict crowd density for given parameters"""
        if self.crowd_predictor is None:
            return {"status": "error", "message": "Model not trained yet. Please train the model first."}
        
        try:
            location_hash = hash(str(location)) % 100
            features = [[float(hour), float(day_of_week), float(location_hash), float(previous_crowd)]]
            prediction = self.crowd_predictor.predict(features)[0]
            
            density_map = {0: 'low', 1: 'medium', 2: 'high'}
            
            # Get confidence (simplified)
            confidence = 0.75 if hasattr(self.crowd_predictor, 'predict_proba') else 0.7
            
            return {
                "status": "success",
                "predicted_density": density_map.get(int(prediction), 'medium'),
                "confidence": float(confidence)
            }
        except Exception as e:
            logger.error(f"Error predicting crowd density: {e}")
            return {"status": "error", "message": str(e)}
    
    def classify_incident(self, title, description, hour):
        """Classify incident type from description"""
        if self.incident_classifier is None:
            return {"status": "error", "message": "Model not trained yet. Please train the model first."}
        
        try:
            text = (str(title) + " " + str(description)).lower()
            word_count = len(text.split())
            char_count = len(text)
            has_emergency_words = int(any(word in text for word in ['fire', 'accident', 'emergency', 'help', 'urgent']))
            has_location_words = int(any(word in text for word in ['road', 'street', 'area', 'building', 'place']))
            
            features = [[float(word_count), float(char_count), float(has_emergency_words), float(has_location_words), float(hour)]]
            prediction = self.incident_classifier.predict(features)[0]
            
            # Ensure prediction is a string
            prediction = str(prediction)
            
            return {
                "status": "success",
                "predicted_type": prediction,
                "confidence": float(0.75)
            }
        except Exception as e:
            logger.error(f"Error classifying incident: {e}")
            return {"status": "error", "message": str(e)}
    
    def detect_anomaly(self, crowd_count, hour, day_of_week):
        """Detect if crowd pattern is anomalous"""
        if self.anomaly_detector is None:
            return {"status": "error", "message": "Model not trained yet. Please train the model first."}
        
        try:
            features = [[float(crowd_count), float(hour), float(day_of_week)]]
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Predict (returns 1 for normal, -1 for anomaly)
            result = self.anomaly_detector.predict(features_scaled)
            
            # Convert numpy.bool_ to Python bool
            is_anomaly = bool(result[0] == -1)
            
            return {
                "status": "success",
                "is_anomaly": is_anomaly,
                "message": "⚠️ Unusual crowd pattern detected!" if is_anomaly else "✅ Normal crowd pattern"
            }
        except Exception as e:
            logger.error(f"Error detecting anomaly: {e}")
            return {"status": "error", "message": str(e)}