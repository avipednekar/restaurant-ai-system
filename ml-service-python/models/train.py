import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error

from utils.data_preprocessing import (
    load_inventory_data, preprocess_inventory_data,
    load_sales_data, preprocess_sales_data
)

# Setup paths
MODELS_DIR = os.path.join(os.path.dirname(__file__))

def train_demand_model():
    """
    Train a Demand Forecasting Model using XGBoost.
    Predicts the 'quantity' of an item based on features like day of week, item_type, etc.
    """
    print("Loading and preprocessing sales data for demand forecasting...")
    try:
        raw_df = load_sales_data()
        df, item_mapping = preprocess_sales_data(raw_df)
    except Exception as e:
        print(f"Error loading sales data: {e}")
        return False
        
    if 'quantity' not in df.columns:
        print("Error: 'quantity' column not found in training data.")
        return False
        
    # Features and Target
    X = df.drop(columns=['quantity'])
    y = df['quantity']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train model
    print("Training Demand Forecasting Model (XGBoost)...")
    model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Demand Model Evaluation - RMSE: {rmse:.2f}, MAE: {mae:.2f}")
    
    # Save model and mappings
    model_path = os.path.join(MODELS_DIR, 'demand_model.joblib')
    mapping_path = os.path.join(MODELS_DIR, 'item_mapping.joblib')
    
    joblib.dump(model, model_path)
    joblib.dump(item_mapping, mapping_path)
    
    # Save feature names for prediction alignment
    features_path = os.path.join(MODELS_DIR, 'demand_features.joblib')
    joblib.dump(list(X.columns), features_path)
    
    print(f"Demand Model saved to {model_path}")
    return True

def train_inventory_model():
    """
    Train an Inventory Optimization Model using Random Forest.
    Predicts the 'Waste_Percentage' based on current stock, daily usage, etc.
    """
    print("Loading and preprocessing inventory data for waste optimization...")
    try:
        raw_df = load_inventory_data()
        df = preprocess_inventory_data(raw_df)
    except Exception as e:
        print(f"Error loading inventory data: {e}")
        return False
        
    target_col = 'Waste_Percentage'
    if target_col not in df.columns:
        print(f"Error: '{target_col}' column not found in inventory data.")
        return False
        
    # Features and Target
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train model
    print("Training Inventory Optimization Model (RandomForest)...")
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Inventory Model Evaluation - RMSE: {rmse:.2f}, MAE: {mae:.2f}")
    
    # Save model and features
    model_path = os.path.join(MODELS_DIR, 'inventory_model.joblib')
    joblib.dump(model, model_path)
    
    features_path = os.path.join(MODELS_DIR, 'inventory_features.joblib')
    joblib.dump(list(X.columns), features_path)
    
    print(f"Inventory Model saved to {model_path}")
    return True

def run_all_training():
    """
    Run all training pipelines.
    """
    print("Starting ML Model Training Pipeline...")
    success_demand = train_demand_model()
    success_inventory = train_inventory_model()
    
    if success_demand and success_inventory:
        print("All models trained successfully.")
        return True
    else:
        print("Some models failed to train.")
        return False

if __name__ == "__main__":
    run_all_training()
