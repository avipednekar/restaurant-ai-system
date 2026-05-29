"""
ML Prediction Engine - Flask Application

A REST API service for food demand prediction and smart billing
powered by machine learning models.
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from config import Config
from models.train import run_all_training
from models.predict import get_prediction_engine

# Load environment variables from .env file
load_dotenv()


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for all routes
    CORS(app)

    register_routes(app)

    return app


def register_routes(app: Flask) -> None:
    """Register all API routes with the Flask application.

    Args:
        app: The Flask application instance.
    """

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint to verify the service is running.

        Returns:
            JSON response with service status.
        """
        return jsonify({
            "status": "healthy",
            "service": "ml-prediction-engine"
        }), 200

    @app.route("/api/predict", methods=["POST"])
    def predict():
        """Endpoint for generating batch predictions.

        Expects a JSON payload with:
        {
            "task": "demand" | "inventory",
            "items": [...]
        }

        Returns:
            JSON response with prediction results.
        """
        data: dict = request.get_json(silent=True) or {}
        
        task = data.get("task")
        items = data.get("items", [])
        
        if not items:
            return jsonify({"error": "No items provided for prediction"}), 400
            
        engine = get_prediction_engine()
        
        if task == "demand":
            predictions = engine.predict_demand(items)
        elif task == "inventory":
            predictions = engine.predict_inventory_waste(items)
        else:
            return jsonify({"error": "Invalid or missing task. Must be 'demand' or 'inventory'"}), 400

        if isinstance(predictions, dict) and "error" in predictions:
            return jsonify(predictions), 500

        return jsonify({
            "success": True,
            "task": task,
            "predictions": predictions
        }), 200

    @app.route("/api/train", methods=["POST"])
    def train():
        """Endpoint for triggering synchronous model training.

        Returns:
            JSON response with training job status.
        """
        success = run_all_training()
        
        # After training, reload the models in the prediction engine
        if success:
            engine = get_prediction_engine()
            engine.load_models()
        
        return jsonify({
            "success": success,
            "message": "Model training completed successfully" if success else "Model training failed",
        }), 200 if success else 500


# Create the application instance
app: Flask = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=True
    )
