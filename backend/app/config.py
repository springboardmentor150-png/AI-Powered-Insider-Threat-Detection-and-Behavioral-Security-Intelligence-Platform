# backend/app/config.py
import os

class Settings:
    PROJECT_NAME: str = "AI Insider Threat Behavioral Intelligence System (ITBIS)"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Security / JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "itbis-super-secret-jwt-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    
    # Databases
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./itbis.db")
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "itbis")
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

settings = Settings()
