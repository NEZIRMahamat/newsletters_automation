from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    groq_api_key: Optional[str] = None
    newsapi_api_key: Optional[str] = None
    playht_api_key: Optional[str] = None
    playht_user_id: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore les champs supplémentaires


settings = Settings()
