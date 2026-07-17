import os

APP_ENV = os.getenv("APP_ENV", "prod")
IS_DEV = APP_ENV == "dev"
