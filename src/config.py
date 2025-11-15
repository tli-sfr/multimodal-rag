"""Configuration management for the RAG system."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment and config files."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )
    
    # LLM Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    openai_embedding_model: str = "text-embedding-3-large"
    anthropic_api_key: str = ""
    cohere_api_key: str = ""
    
    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password123"
    
    # Qdrant Configuration
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str = ""
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Application Settings
    log_level: str = "INFO"
    environment: str = "development"
    max_workers: int = 4
    
    # Ingestion Settings
    chunk_size: int = 512
    chunk_overlap: int = 50
    max_file_size_mb: int = 100
    
    # Search Settings
    top_k_results: int = 10
    similarity_threshold: float = 0.7
    rerank_top_k: int = 5
    
    # Evaluation Settings
    eval_dataset_path: str = "data/eval/test_queries.json"
    eval_output_path: str = "data/eval/results"
    
    # Security
    enable_auth: bool = False
    secret_key: str = "your_secret_key_here"
    allowed_origins: str = "http://localhost:8501"
    
    # Observability
    enable_metrics: bool = True
    prometheus_port: int = 8000
    enable_tracing: bool = False


class Config:
    """Configuration loader for YAML config files."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize configuration.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key (e.g., 'llm.model')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Configuration section as dictionary
        """
        return self._config.get(section, {})
    
    @property
    def all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._config


# Global instances
settings = Settings()
config = Config() if Path("config/config.yaml").exists() else None


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def get_config() -> Optional[Config]:
    """Get YAML configuration."""
    return config

