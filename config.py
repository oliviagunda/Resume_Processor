"""Configuration management for the AI internship project."""
import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = 'localhost'
    user: str = 'root'
    password: str = ''
    database: str = 'interviewees'
    port: int = 3306


@dataclass
class AppConfig:
    """Application configuration settings."""
    resume_folder: str = 'resumes'
    test_data_folder: str = 'test_data'
    log_level: str = 'INFO'


class Config:
    """Central configuration manager."""
    
    def __init__(self):
        self.db = DatabaseConfig()
        self.app = AppConfig()
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        self.db.host = os.getenv('DB_HOST', self.db.host)
        self.db.user = os.getenv('DB_USER', self.db.user)
        self.db.password = os.getenv('DB_PASSWORD', self.db.password)
        self.db.database = os.getenv('DB_NAME', self.db.database)
        self.db.port = int(os.getenv('DB_PORT', self.db.port))
        
        self.app.resume_folder = os.getenv('RESUME_FOLDER', self.app.resume_folder)
        self.app.test_data_folder = os.getenv('TEST_DATA_FOLDER', self.app.test_data_folder)
        self.app.log_level = os.getenv('LOG_LEVEL', self.app.log_level)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return {
            'database': {
                'host': self.db.host,
                'user': self.db.user,
                'password': self.db.password,
                'database': self.db.database,
                'port': self.db.port
            },
            'app': {
                'resume_folder': self.app.resume_folder,
                'test_data_folder': self.app.test_data_folder,
                'log_level': self.app.log_level
            }
        }


# Global configuration instance
config = Config()