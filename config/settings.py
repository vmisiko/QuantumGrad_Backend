import os
from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL = 'sqlite://db.sqlite3'
    SECRET_KEY = 'myjwtsecret'
    APP_NAME = 'My App'
    REGISTRATION_TOKEN_LIFETIME = 60 * 60
    TOKEN_ALGORITHM = 'HS256'
    SMTP_SERVER = '455'
    MAIL_SENDER = 'noreply@example.com'
    API_PREFIX = '/api'
    HOST = 'localhost'
    PORT = 8000
    BASE_URL = 'http://localhost:8080'
    MODELS = [
        'models.user',
        'aerich.models',
    ]

    class Config:
        case_sensitive: bool = True


@lru_cache()
def get_settings():
    return Settings()
