from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ARGUS"
    DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    JWT_SECRET_KEY: str
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()