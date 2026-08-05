from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Vetra"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/vetra",
    )

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GROQ_TRANSCRIBE_API_KEY: str = os.getenv("GROQ_TRANSCRIBE_API_KEY", "")
    GROQ_WHISPER_MODEL: str = "whisper-large-v3"

    # WhatsApp Cloud API (Meta)
    AK_WHATSAPP__ACCESS_TOKEN: str = os.getenv("AK_WHATSAPP__ACCESS_TOKEN", "")
    AK_WHATSAPP__PHONE_NUMBER_ID: str = os.getenv("AK_WHATSAPP__PHONE_NUMBER_ID", "")
    AK_WHATSAPP__API_VERSION: str = os.getenv("AK_WHATSAPP__API_VERSION", "v26.0")
    # Approved template used for visit notifications. Empty => fall back to free-form
    # text (which only delivers inside a 24h user session). Set to an APPROVED
    # template name so business-initiated notifications always deliver.
    AK_WHATSAPP__TEMPLATE_NAME: str = os.getenv("AK_WHATSAPP__TEMPLATE_NAME", "")
    AK_WHATSAPP__TEMPLATE_LANGUAGE: str = os.getenv("AK_WHATSAPP__TEMPLATE_LANGUAGE", "en_US")

    # Public magic links / notification URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    NOTIFICATION_SECRET: str = os.getenv("NOTIFICATION_SECRET", "vetra-notification-secret")
    MAGIC_LINK_TTL_DAYS: int = 7

    class Config:
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
