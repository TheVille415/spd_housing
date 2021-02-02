"""Initialize Config class to access environment variables."""
import os


class Config(object):
    """Set environment variables."""

    DEBUG = True

<<<<<<< HEAD
    MONGO_URI = os.getenv("MONGODB_URI")
=======
    MONGODB_URI = os.getenv("MONGODB_URI")
>>>>>>> 60a31c1587004a0335b6e61810d1ffe354617a22
    # API_KEY = Zillow API key access goes here
