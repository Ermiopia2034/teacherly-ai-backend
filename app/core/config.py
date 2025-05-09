from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    # API Information
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Teacherly AI"
    
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google Gemini API
    GEMINI_API_KEY: Optional[str] = None
    
    # OCR.space API
    OCR_API_KEY: Optional[str] = None
    
    # SMTP Server
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # ChromaDB
    CHROMA_DB_PATH: str = ".chromadb"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings() 