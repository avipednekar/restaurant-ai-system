import sys
import os
import json

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from models.train import run_all_training
from models.predict import get_prediction_engine

def test_ml_pipeline():
    print("--- Testing Training ---")
    success = run_all_training()
    if not success:
        print("Training failed!")
        return
        
    print("\n--- Testing Prediction ---")
    engine = get_prediction_engine()
    engine.load_models()
    
    # Dummy batch for demand forecasting
    demand_batch = [
        {"item_name": "Vadapav", "item_type": "Fastfood", "day_of_week": 2, "month": 6, "is_weekend": 0},
        {"item_name": "Cold coffee", "item_type": "Beverages", "day_of_week": 5, "month": 6, "is_weekend": 1},
        {"item_name": "UnknownItem", "item_type": "Fastfood", "day_of_week": 1, "month": 6, "is_weekend": 0}
    ]
    print("\nDemand Predictions:")
    demand_preds = engine.predict_demand(demand_batch)
    print(json.dumps(demand_preds, indent=2))
    
    # Dummy batch for inventory optimization
    inventory_batch = [
        {"Current_Stock": 15, "Daily_Usage": 5, "Lead_Time": 2},
        {"Current_Stock": 2, "Daily_Usage": 10, "Lead_Time": 1}
    ]
    print("\nInventory Predictions:")
    inventory_preds = engine.predict_inventory_waste(inventory_batch)
    print(json.dumps(inventory_preds, indent=2))
    
    print("\nAll ML tests completed successfully.")

if __name__ == "__main__":
    test_ml_pipeline()
