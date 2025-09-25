from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""

    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "recruitment_portal"

    # Application settings
    APP_NAME: str = "Recruitment Portal"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # JWT settings
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email settings
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587  # STARTTLS
    EMAIL_SECURE: bool = True
    EMAIL_USER: str = "ecell@kiet.edu"
    EMAIL_PASS: str = "xlidhflhxuqlvhcz"
    EMAIL_FROM: str = "ECELL KIET <ecell@kiet.edu>"
    EMAIL_TEST_MODE: bool = False


    # Environment
    ENVIRONMENT: str = "development"


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create global settings object
settings = Settings()
