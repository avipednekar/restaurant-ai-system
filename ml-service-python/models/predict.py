import os
import joblib
import pandas as pd
import numpy as np

MODELS_DIR = os.path.dirname(__file__)

class PredictionEngine:
    def __init__(self):
        self.demand_model = None
        self.item_mapping = None
        self.demand_features = None
        
        self.inventory_model = None
        self.inventory_features = None
        
        self.load_models()
        
    def load_models(self):
        """Loads all serialized models and mappings."""
        try:
            self.demand_model = joblib.load(os.path.join(MODELS_DIR, 'demand_model.joblib'))
            self.item_mapping = joblib.load(os.path.join(MODELS_DIR, 'item_mapping.joblib'))
            self.demand_features = joblib.load(os.path.join(MODELS_DIR, 'demand_features.joblib'))
            
            self.inventory_model = joblib.load(os.path.join(MODELS_DIR, 'inventory_model.joblib'))
            self.inventory_features = joblib.load(os.path.join(MODELS_DIR, 'inventory_features.joblib'))
            print("Models loaded successfully.")
        except Exception as e:
            print(f"Warning: Models could not be loaded. Please train models first. Error: {e}")
            
    def predict_demand(self, items):
        """
        Predicts demand for a batch of items.
        Expected items format: list of dicts. 
        Example: [{'item_name': 'Vadapav', 'item_type': 'Fastfood', 'day_of_week': 2, ...}]
        """
        if self.demand_model is None:
            return {"error": "Demand model not loaded."}
            
        df = pd.DataFrame(items)
        
        # Apply item_name mapping if it exists
        if 'item_name' in df.columns and self.item_mapping is not None:
            df['item_name'] = df['item_name'].map(self.item_mapping).fillna(-1)
            
        # Basic categorical encoding simulation (In production, use OneHotEncoder/LabelEncoder saved during training)
        for col in df.columns:
            if df[col].dtype == 'object' and col != 'item_name':
                df[col] = df[col].astype('category').cat.codes
                
        # Ensure all expected features are present, fill missing with 0
        for feature in self.demand_features:
            if feature not in df.columns:
                df[feature] = 0
                
        # Reorder columns to match training data
        X = df[self.demand_features]
        
        # Predict
        predictions = self.demand_model.predict(X)
        
        results = []
        for i, pred in enumerate(predictions):
            results.append({
                "item_index": i,
                "predicted_quantity": float(max(0, round(pred, 2))) # Demand can't be negative
            })
            
        return results

    def predict_inventory_waste(self, inventory_items):
        """
        Predicts waste percentage and recommendations for a batch of inventory items.
        Expected format: list of dicts.
        """
        if self.inventory_model is None:
            return {"error": "Inventory model not loaded."}
            
        df = pd.DataFrame(inventory_items)
        
        # Categorical encoding fallback
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype('category').cat.codes
                
        # Ensure all expected features are present
        for feature in self.inventory_features:
            if feature not in df.columns:
                df[feature] = 0
                
        X = df[self.inventory_features]
        
        predictions = self.inventory_model.predict(X)
        
        results = []
        for i, pred in enumerate(predictions):
            results.append({
                "item_index": i,
                "predicted_waste_percentage": float(max(0, round(pred, 2))),
                "action_recommended": "Reduce Reorder Level" if pred > 5.0 else "Stock is Optimal"
            })
            
        return results

# Singleton instance
engine = PredictionEngine()

def get_prediction_engine():
    return engine
