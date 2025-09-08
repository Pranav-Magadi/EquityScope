"""
Configuration Management for EquityScope Backend
Handles environment variables and application settings
"""

import os
from pathlib import Path
from typing import Optional

class Settings:
    """Application configuration settings"""
    
    # Application
    APP_NAME: str = "EquityScope"
    VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    # File Storage Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: str = os.getenv("DATA_DIR", str(BASE_DIR / "data"))
    CACHE_DIR: str = os.getenv("CACHE_DIR", str(BASE_DIR / "cache"))
    LOG_DIR: str = os.getenv("LOG_DIR", str(BASE_DIR / "logs"))
    
    # Database Configuration
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "file_json")  # file_json, sqlite, postgresql
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    
    # CORS
    CORS_ORIGINS: list = [
        origin.strip() 
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    ]
    
    # External APIs
    CLAUDE_API_KEY: Optional[str] = os.getenv("CLAUDE_API_KEY")
    FINANCIAL_DATA_API_KEY: Optional[str] = os.getenv("FINANCIAL_DATA_API_KEY")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    
    # Caching
    CACHE_TTL_HOURS: int = int(os.getenv("CACHE_TTL_HOURS", 6))
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __init__(self):
        """Create necessary directories"""
        for directory in [self.DATA_DIR, self.CACHE_DIR, self.LOG_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True)

# Global settings instance
settings = Settings()

# File storage structure will be:
# data/
# ├── users/
# │   ├── users.json
# │   ├── sessions.json
# │   └── api_keys.json
# ├── cache/
# │   ├── financial_data/
# │   ├── analysis_results/
# │   └── news_sentiment/
# └── logs/
#     ├── app.log
#     └── error.log