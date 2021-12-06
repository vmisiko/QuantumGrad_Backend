from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from config.settings import get_settings

settings = get_settings()

DB_CONFIG = {
    "connections": {
        "default": settings.DATABASE_URL
    },
    "apps": {
        "models": {
            "models": settings.MODELS
        }
    }
}

def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        config=DB_CONFIG,
        generate_schemas=False,
    )

