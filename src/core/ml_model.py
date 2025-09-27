"""
Machine Learning model for intrusion detection
"""
import os
import pandas as pd
import joblib
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from pathlib import Path
from config.settings import MODEL_FILE, LOGIN_ATTEMPTS_LOG, MODEL_FEATURES
from src.core.logger import get_logger

logger = get_logger(__name__)

class IntrusionModel:
    """Machine Learning model for detecting intrusions"""
    
    def __init__(self):
        self.model = None
        self.model_file = MODEL_FILE
        self.features = MODEL_FEATURES
        self.is_trained = False
        self._load_model()
    
    def _load_model(self):
        """Load existing model if available"""
        try:
            if self.model_file.exists():
                self.model = joblib.load(self.model_file)
                self.is_trained = True
                logger.info(f"Loaded existing model from {self.model_file}")
            else:
                logger.info("No existing model found. Model needs to be trained.")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            self.is_trained = False
    
    def _prepare_features(self, data):
        """Prepare features for training or prediction"""
        if isinstance(data, pd.DataFrame):
            # For training data
            features = pd.DataFrame()
            features['username_len'] = data['username'].str.len()
            features['password_len'] = data['password'].str.len()
            features['timestamp'] = pd.to_datetime(data['timestamp']).astype(int) / 10**9
            return features
        else:
            # For single prediction - data should be [username_len, password_len, timestamp]
            return np.array(data).reshape(1, -1)
    
    def _generate_labels(self, data):
        """Generate labels for training (simplified heuristic)"""
        # This is a simplified labeling strategy
        # In a real system, you would have actual labeled data
        labels = []
        for _, row in data.iterrows():
            # Label as attack (1) if:
            # - Username is common attack username
            # - Password is weak/common
            # - IP shows suspicious patterns
            is_attack = 0
            
            common_attack_usernames = ['admin', 'root', 'administrator', 'test']
            weak_passwords = ['123', 'password', 'admin', 'test', '123456']
            
            if (row['username'].lower() in common_attack_usernames or 
                row['password'] in weak_passwords or
                len(row['password']) < 4):
                is_attack = 1
            
            labels.append(is_attack)
        
        return np.array(labels)
    
    def train(self, data_file=None):
        """Train the intrusion detection model"""
        try:
            if data_file is None:
                data_file = LOGIN_ATTEMPTS_LOG
            
            if not Path(data_file).exists():
                logger.error(f"Training data file not found: {data_file}")
                return False
            
            # Load data
            data = pd.read_csv(data_file, names=['ip', 'username', 'password', 'timestamp'])
            
            if len(data) < 10:
                logger.warning("Insufficient data for training (need at least 10 samples)")
                return False
            
            # Prepare features and labels
            X = self._prepare_features(data)
            y = self._generate_labels(data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            logger.info(f"Model training completed.")
            logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
            
            # Save model
            self.model_file.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(self.model, self.model_file)
            self.is_trained = True
            
            logger.info(f"Model saved to {self.model_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False
    
    def predict(self, username, password, timestamp=None):
        """Predict if a login attempt is an attack"""
        try:
            if not self.is_trained or self.model is None:
                logger.warning("Model not trained. Cannot make predictions.")
                return 0  # Default to no attack
            
            if timestamp is None:
                timestamp = datetime.now().timestamp()
            elif isinstance(timestamp, str):
                timestamp = pd.to_datetime(timestamp).timestamp()
            
            # Prepare features
            features = [[len(username), len(password), timestamp]]
            
            # Make prediction
            prediction = self.model.predict(features)[0]
            probability = self.model.predict_proba(features)[0]
            
            logger.debug(f"Prediction for {username}:{password} = {prediction} (prob: {probability})")
            return prediction
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return 0  # Default to no attack on error
    
    def get_feature_importance(self):
        """Get feature importance from the trained model"""
        if not self.is_trained or self.model is None:
            return None
        
        try:
            importance = self.model.feature_importances_
            feature_names = ['username_length', 'password_length', 'timestamp']
            return dict(zip(feature_names, importance))
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return None
    
    def model_info(self):
        """Get information about the current model"""
        if not self.is_trained or self.model is None:
            return {"status": "Not trained", "model_file": str(self.model_file)}
        
        info = {
            "status": "Trained",
            "model_type": type(self.model).__name__,
            "model_file": str(self.model_file),
            "features": self.features,
            "feature_importance": self.get_feature_importance()
        }
        
        if hasattr(self.model, 'n_estimators'):
            info['n_estimators'] = self.model.n_estimators
        
        return info

# Global model instance
intrusion_model = IntrusionModel()
