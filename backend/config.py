from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "mongodb://user:password@localhost:27017"
    MONGO_DB_NAME: str = "edtech"
    SECRET_KEY: str = "your-secret-key"
    API_LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

settings = Settings() 