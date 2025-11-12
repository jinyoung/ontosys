from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App Settings
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: str = "http://localhost:5173"
    
    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "ontosys123"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    
    # Upload Settings
    max_upload_size: int = 10485760  # 10MB
    upload_dir: str = "./uploads"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()



