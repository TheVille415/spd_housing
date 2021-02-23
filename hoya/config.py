"""Initialize Config class to access environment variables."""
import os


class Config(object):
    """Set environment variables."""

    DEBUG = True

    MONGO_URI = os.getenv("MONGO_URI")
