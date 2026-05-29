"""
generate_predictions_db.py
==========================
Generates predictions using the trained ML models (XGBoost for demand,
RandomForest for inventory waste) and stores them in the MySQL database tables
`predictions` and `inventory_predictions`.

This ensures that the Analytics APIs (GET /api/analytics/demand/range and
GET /api/analytics/inventory/range) return accurate predictions along with actuals.

Usage:
    python generate_predictions_db.py
"""

import os
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from models.predict import get_prediction_engine

# Load environment variables
load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "restaurant_ai_db")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

def get_engine():
    engine = create_engine(DATABASE_URL, echo=False)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return engine

def generate_predictions():
    print("=" * 60)
    print("RESTAURANT AI - GENERATING DATABASE PREDICTIONS")
    print("=" * 60)
    
    engine = get_engine()
    print("[OK] Database connection established.")
    
    pred_engine = get_prediction_engine()
    pred_engine.load_models()
    
    if pred_engine.demand_model is None or pred_engine.inventory_model is None:
        print("[ERROR] ML Models are not trained or could not be loaded!")
        print("Please run model training first: python models/train.py")
        return
        
    # ============================================================
    # PART 1: GENERATE DEMAND PREDICTIONS
    # ============================================================
    print("\n--- Part 1: Generating Demand Predictions ---")
    
    # Fetch menu items and ml_features
    with engine.connect() as conn:
        menu_items_df = pd.read_sql("SELECT id, item_name, item_type FROM menu_items", conn)
        features_df = pd.read_sql("SELECT id, menu_item_id, sale_date, day_of_week, is_weekend, month, quantity_sold, price FROM ml_features", conn)
        
    if features_df.empty:
        print("[WARNING] No records found in ml_features table. Please run import_and_preprocess.py first.")
    else:
        # Create item_id to name/type mappings
        item_name_map = dict(zip(menu_items_df["id"], menu_items_df["item_name"]))
        item_type_map = dict(zip(menu_items_df["id"], menu_items_df["item_type"]))
        
        # Build batch items for prediction
        batch_items = []
        for idx, row in features_df.iterrows():
            menu_id = int(row["menu_item_id"])
            batch_items.append({
                "item_name": item_name_map.get(menu_id, "Unknown"),
                "item_type": item_type_map.get(menu_id, "Fastfood"),
                "day_of_week": int(row["day_of_week"]),
                "month": int(row["month"]),
                "is_weekend": int(row["is_weekend"]),
                "item_price": float(row["price"]),
                "price": float(row["price"])
            })
            
        print(f"Running demand model prediction for {len(batch_items)} records...")
        predictions = pred_engine.predict_demand(batch_items)
        
        # Prepare records for insertion
        prediction_records = []
        for idx, row in features_df.iterrows():
            pred_qty = predictions[idx]["predicted_quantity"]
            prediction_records.append({
                "menu_item_id": int(row["menu_item_id"]),
                "prediction_date": row["sale_date"].strftime("%Y-%m-%d"),
                "predicted_quantity": float(pred_qty),
                "confidence_lower": float(round(pred_qty * 0.9, 2)),
                "confidence_upper": float(round(pred_qty * 1.1, 2)),
                "model_name": "XGBoost",
                "model_version": "1.0",
                "is_festival_day": False,
                "actual_quantity": float(row["quantity_sold"])
            })
            
        # Bulk Insert (using ON DUPLICATE KEY UPDATE to avoid constraints issues)
        print("Inserting demand predictions into MySQL...")
        with engine.begin() as conn:
            # Clear old predictions to avoid duplicate key issues if needed, or do it gracefully
            conn.execute(text("DELETE FROM predictions WHERE model_name = 'XGBoost'"))
            
            insert_query = text("""
                INSERT INTO predictions 
                (menu_item_id, prediction_date, predicted_quantity, confidence_lower, confidence_upper, model_name, model_version, is_festival_day, actual_quantity)
                VALUES 
                (:menu_item_id, :prediction_date, :predicted_quantity, :confidence_lower, :confidence_upper, :model_name, :model_version, :is_festival_day, :actual_quantity)
            """)
            
            # Batch inserts of 1000 records
            batch_size = 1000
            for i in range(0, len(prediction_records), batch_size):
                chunk = prediction_records[i : i + batch_size]
                conn.execute(insert_query, chunk)
                
        print(f"[SUCCESS] Generated and saved {len(prediction_records)} demand predictions.")

    # ============================================================
    # PART 2: GENERATE INVENTORY PREDICTIONS
    # ============================================================
    print("\n--- Part 2: Generating Inventory Predictions ---")
    
    # Fetch inventory records
    with engine.connect() as conn:
        inventory_df = pd.read_sql("SELECT id, item_name, category, subcategory, unit, current_stock, reorder_level, daily_usage, lead_time_days, price_per_unit, supplier_name, seasonal_factor, waste_pct, record_date FROM inventory", conn)
        
    if inventory_df.empty:
        print("[WARNING] No records found in inventory table. Please run import_and_preprocess.py first.")
    else:
        # Build batch items for prediction
        # The RandomForest model is trained on preprocessed fields:
        # 'Current_Stock', 'Reorder_Level', 'Daily_Usage', 'Lead_Time', 'Price_per_Unit', 'Seasonal_Factor'
        # Let's map category, subcategory, unit, supplier_name if they are in features
        
        batch_inv = []
        for idx, row in inventory_df.iterrows():
            batch_inv.append({
                "Category": row["category"],
                "Subcategory": row["subcategory"],
                "Unit": row["unit"],
                "Supplier_Name": row["supplier_name"],
                "Current_Stock": float(row["current_stock"]),
                "Reorder_Level": float(row["reorder_level"]),
                "Daily_Usage": float(row["daily_usage"]),
                "Lead_Time": int(row["lead_time_days"]),
                "Price_per_Unit": float(row["price_per_unit"]),
                "Seasonal_Factor": float(row["seasonal_factor"])
            })
            
        print(f"Running inventory waste model prediction for {len(batch_inv)} records...")
        predictions_inv = pred_engine.predict_inventory_waste(batch_inv)
        
        # Prepare records for insertion
        inv_prediction_records = []
        for idx, row in inventory_df.iterrows():
            pred_waste = predictions_inv[idx]["predicted_waste_percentage"]
            action = predictions_inv[idx]["action_recommended"]
            
            inv_prediction_records.append({
                "inventory_item_name": row["item_name"],
                "prediction_date": row["record_date"].strftime("%Y-%m-%d"),
                "current_stock": float(row["current_stock"]),
                "daily_usage": float(row["daily_usage"]),
                "predicted_waste_percentage": float(pred_waste),
                "action_recommended": action,
                "model_name": "RandomForest",
                "model_version": "1.0",
                "actual_waste_percentage": float(row["waste_pct"])
            })
            
        # Bulk Insert
        print("Inserting inventory predictions into MySQL...")
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM inventory_predictions WHERE model_name = 'RandomForest'"))
            
            insert_query = text("""
                INSERT INTO inventory_predictions 
                (inventory_item_name, prediction_date, current_stock, daily_usage, predicted_waste_percentage, action_recommended, model_name, model_version, actual_waste_percentage)
                VALUES 
                (:inventory_item_name, :prediction_date, :current_stock, :daily_usage, :predicted_waste_percentage, :action_recommended, :model_name, :model_version, :actual_waste_percentage)
            """)
            
            # Batch inserts of 1000 records
            batch_size = 1000
            for i in range(0, len(inv_prediction_records), batch_size):
                chunk = inv_prediction_records[i : i + batch_size]
                conn.execute(insert_query, chunk)
                
        print(f"[SUCCESS] Generated and saved {len(inv_prediction_records)} inventory predictions.")
        
    print("\n" + "=" * 60)
    print("PREDICTIONS GENERATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    generate_predictions()
