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
        """Placeholder endpoint for generating predictions.

        Expects a JSON payload with input features for the ML model.

        Returns:
            JSON response with prediction results.
        """
        data: dict = request.get_json(silent=True) or {}

        # TODO: Implement actual prediction logic
        return jsonify({
            "success": True,
            "message": "Prediction endpoint placeholder",
            "input_received": data,
            "predictions": []
        }), 200

    @app.route("/api/train", methods=["POST"])
    def train():
        """Placeholder endpoint for triggering model training.

        Expects a JSON payload with training configuration parameters.

        Returns:
            JSON response with training job status.
        """
        data: dict = request.get_json(silent=True) or {}

        # TODO: Implement actual training logic
        return jsonify({
            "success": True,
            "message": "Training endpoint placeholder",
            "config_received": data,
            "job_status": "pending"
        }), 200


# Create the application instance
app: Flask = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=True
    )
