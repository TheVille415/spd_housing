"""Initialize Config class to access environment variables."""
import os


class Config(object):
    """Set environment variables."""

    DEBUG = True

    MONGO_URI = os.getenv("MONGODB_URI")
    # API_KEY = Zillow API key access goes here
