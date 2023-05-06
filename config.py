# config.py
import os

# Auth0 configuration
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.environ.get("AUTH0_CALLBACK_URL")
AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE")

# MongoDB Atlas configuration
MONGO_URI = os.environ.get("MONGO_URI")

# JWT configuration
SECRET_KEY = os.environ.get("SECRET_KEY")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
