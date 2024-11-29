
import sys
import os

# Set the correct path to import the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db, create_app  # Import the Flask app and SQLAlchemy instance
from app.models import *  # Import all models (replace * with specific model names if needed)

# Initialize the Flask application
app = create_app()

# Create the database and tables within the app context
with app.app_context():
    db.create_all()
    print("Database tables created!")

    