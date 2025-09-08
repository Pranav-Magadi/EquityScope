"""
Database Structure and Migration System
Supports both file-based JSON storage (development) and PostgreSQL (production)
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
import sqlite3
import asyncpg
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, DateTime, Boolean, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

class DatabaseType(str, Enum):
    """Supported database types"""
    FILE_JSON = "file_json"      # Development: JSON files
    SQLITE = "sqlite"            # Local testing: SQLite
    POSTGRESQL = "postgresql"    # Production: PostgreSQL
    MONGODB = "mongodb"          # Alternative: MongoDB

class DatabaseManager:
    """Multi-database manager supporting different storage backends"""
    
    def __init__(self, db_type: DatabaseType = None):
        self.db_type = db_type or DatabaseType(settings.DATABASE_TYPE)
        self.connection = None
        self.data_dir = Path(settings.DATA_DIR)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    async def initialize(self):
        """Initialize database based on type"""
        if self.db_type == DatabaseType.FILE_JSON:
            await self._init_file_storage()
        elif self.db_type == DatabaseType.SQLITE:
            await self._init_sqlite()
        elif self.db_type == DatabaseType.POSTGRESQL:
            await self._init_postgresql()
        elif self.db_type == DatabaseType.MONGODB:
            await self._init_mongodb()
    
    async def _init_file_storage(self):
        """Initialize file-based JSON storage"""
        # Create directory structure
        for subdir in ['users', 'cache', 'analytics', 'backups']:
            (self.data_dir / subdir).mkdir(exist_ok=True)
        
        # Initialize data files
        data_files = {
            'users/users.json': [],
            'users/sessions.json': [],
            'users/api_keys.json': [],
            'analytics/usage_stats.json': [],
            'analytics/system_metrics.json': {},
            'cache/cache_index.json': {}
        }
        
        for file_path, default_data in data_files.items():
            full_path = self.data_dir / file_path
            if not full_path.exists():
                with open(full_path, 'w') as f:
                    json.dump(default_data, f, indent=2)
    
    async def _init_sqlite(self):
        """Initialize SQLite database"""
        db_path = self.data_dir / "equityscope.db"
        self.connection = sqlite3.connect(str(db_path))
        
        # Create tables
        await self._create_sqlite_tables()
    
    async def _init_postgresql(self):
        """Initialize PostgreSQL connection"""
        connection_string = (
            f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )
        
        self.connection = await asyncpg.connect(connection_string)
        await self._create_postgresql_tables()
    
    async def _init_mongodb(self):
        """Initialize MongoDB connection"""
        # MongoDB implementation would go here
        pass
    
    async def _create_sqlite_tables(self):
        """Create SQLite tables"""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT,
            company TEXT,
            status TEXT DEFAULT 'pending_verification',
            email_verified BOOLEAN DEFAULT FALSE,
            verification_token TEXT,
            tier TEXT DEFAULT 'free',
            subscription_start DATETIME,
            subscription_end DATETIME,
            stripe_customer_id TEXT,
            total_analyses INTEGER DEFAULT 0,
            monthly_analyses INTEGER DEFAULT 0,
            last_analysis DATETIME,
            rate_limit_window_start DATETIME,
            rate_limit_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
        """)
        
        # Sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # API Keys table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            key_hash TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            last_used DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Usage analytics table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            event_type TEXT NOT NULL,
            event_data JSON,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Cache metadata table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache_metadata (
            cache_key TEXT PRIMARY KEY,
            cache_type TEXT NOT NULL,
            ticker TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            file_path TEXT,
            size_bytes INTEGER,
            hit_count INTEGER DEFAULT 0,
            last_accessed DATETIME
        )
        """)
        
        self.connection.commit()
    
    async def _create_postgresql_tables(self):
        """Create PostgreSQL tables"""
        await self.connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name VARCHAR(255),
            company VARCHAR(255),
            status VARCHAR(50) DEFAULT 'pending_verification',
            email_verified BOOLEAN DEFAULT FALSE,
            verification_token TEXT,
            tier VARCHAR(20) DEFAULT 'free',
            subscription_start TIMESTAMP,
            subscription_end TIMESTAMP,
            stripe_customer_id VARCHAR(255),
            total_analyses INTEGER DEFAULT 0,
            monthly_analyses INTEGER DEFAULT 0,
            last_analysis TIMESTAMP,
            rate_limit_window_start TIMESTAMP,
            rate_limit_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            last_login TIMESTAMP
        )
        """)
        
        await self.connection.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id),
            ip_address INET,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            last_activity TIMESTAMP DEFAULT NOW(),
            is_active BOOLEAN DEFAULT TRUE
        )
        """)
        
        await self.connection.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id),
            name VARCHAR(255) NOT NULL,
            key_hash TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            last_used TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            expires_at TIMESTAMP
        )
        """)
        
        await self.connection.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES users(id),
            event_type VARCHAR(100) NOT NULL,
            event_data JSONB,
            timestamp TIMESTAMP DEFAULT NOW(),
            ip_address INET,
            user_agent TEXT
        )
        """)
        
        await self.connection.execute("""
        CREATE TABLE IF NOT EXISTS cache_metadata (
            cache_key VARCHAR(255) PRIMARY KEY,
            cache_type VARCHAR(50) NOT NULL,
            ticker VARCHAR(20),
            created_at TIMESTAMP DEFAULT NOW(),
            expires_at TIMESTAMP,
            file_path TEXT,
            size_bytes BIGINT,
            hit_count INTEGER DEFAULT 0,
            last_accessed TIMESTAMP
        )
        """)
        
        # Create indexes for performance
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_cache_ticker ON cache_metadata(ticker)")
        await self.connection.execute("CREATE INDEX IF NOT EXISTS idx_cache_type ON cache_metadata(cache_type)")

class FileDatabase:
    """File-based database implementation for development"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, table: str) -> Path:
        """Get file path for table"""
        return self.data_dir / f"{table}.json"
    
    def _load_table(self, table: str) -> List[Dict[str, Any]]:
        """Load table data from JSON file"""
        file_path = self._get_file_path(table)
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_table(self, table: str, data: List[Dict[str, Any]]):
        """Save table data to JSON file"""
        file_path = self._get_file_path(table)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def insert(self, table: str, record: Dict[str, Any]) -> bool:
        """Insert record into table"""
        data = self._load_table(table)
        data.append(record)
        self._save_table(table, data)
        return True
    
    def find_one(self, table: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one record matching query"""
        data = self._load_table(table)
        for record in data:
            if all(record.get(k) == v for k, v in query.items()):
                return record
        return None
    
    def find_many(self, table: str, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find multiple records matching query"""
        data = self._load_table(table)
        if not query:
            return data
        
        results = []
        for record in data:
            if all(record.get(k) == v for k, v in query.items()):
                results.append(record)
        return results
    
    def update_one(self, table: str, query: Dict[str, Any], 
                   update: Dict[str, Any]) -> bool:
        """Update one record matching query"""
        data = self._load_table(table)
        for i, record in enumerate(data):
            if all(record.get(k) == v for k, v in query.items()):
                data[i].update(update)
                self._save_table(table, data)
                return True
        return False
    
    def delete_one(self, table: str, query: Dict[str, Any]) -> bool:
        """Delete one record matching query"""
        data = self._load_table(table)
        for i, record in enumerate(data):
            if all(record.get(k) == v for k, v in query.items()):
                data.pop(i)
                self._save_table(table, data)
                return True
        return False

class DatabaseConfig:
    """Database configuration for different environments"""
    
    @staticmethod
    def get_development_config() -> Dict[str, Any]:
        """Get development database configuration"""
        return {
            "type": DatabaseType.FILE_JSON,
            "data_dir": "./data",
            "backup_enabled": True,
            "backup_interval_hours": 24
        }
    
    @staticmethod
    def get_testing_config() -> Dict[str, Any]:
        """Get testing database configuration"""
        return {
            "type": DatabaseType.SQLITE,
            "database_path": ":memory:",  # In-memory for tests
            "data_dir": "./test_data"
        }
    
    @staticmethod
    def get_production_config() -> Dict[str, Any]:
        """Get production database configuration"""
        return {
            "type": DatabaseType.POSTGRESQL,
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "equityscope"),
            "username": os.getenv("DB_USER", "equityscope"),
            "password": os.getenv("DB_PASSWORD", ""),
            "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "ssl_mode": os.getenv("DB_SSL_MODE", "require")
        }

# Migration utilities
class DatabaseMigration:
    """Handle database migrations between different storage systems"""
    
    @staticmethod
    async def migrate_file_to_postgresql(source_dir: Path, target_db: DatabaseManager):
        """Migrate from file-based storage to PostgreSQL"""
        file_db = FileDatabase(source_dir)
        
        # Migrate users
        users = file_db.find_many("users")
        for user in users:
            # Convert datetime strings to proper timestamps
            for date_field in ['created_at', 'updated_at', 'last_login', 'subscription_start', 'subscription_end']:
                if user.get(date_field):
                    user[date_field] = datetime.fromisoformat(user[date_field].replace('Z', '+00:00'))
        
        # Insert into PostgreSQL (implementation depends on async library)
        # This would use target_db.connection to insert records
        
    @staticmethod
    async def backup_database(db_manager: DatabaseManager, backup_path: Path):
        """Create database backup"""
        if db_manager.db_type == DatabaseType.FILE_JSON:
            # Simply copy files
            import shutil
            shutil.copytree(db_manager.data_dir, backup_path)
        elif db_manager.db_type == DatabaseType.POSTGRESQL:
            # Use pg_dump
            import subprocess
            subprocess.run([
                "pg_dump", 
                f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
                "-f", str(backup_path / "backup.sql")
            ])

# Database schema versioning
DATABASE_VERSION = "1.0.0"
SCHEMA_MIGRATIONS = {
    "1.0.0": "Initial schema with users, sessions, api_keys, analytics, cache_metadata"
}

def get_database_info() -> Dict[str, Any]:
    """Get current database configuration and status"""
    return {
        "type": settings.DATABASE_TYPE,
        "version": DATABASE_VERSION,
        "data_directory": str(Path(settings.DATA_DIR).absolute()),
        "supported_types": [db_type.value for db_type in DatabaseType],
        "schema_version": DATABASE_VERSION,
        "available_migrations": list(SCHEMA_MIGRATIONS.keys())
    }