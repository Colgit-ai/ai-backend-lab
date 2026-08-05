from pydantic_settings import BaseSettings, SettingsConfigDict

# BaseSettings automatically converts and validates data types (like integers or booleans) and crashes early at startup if variables are missing. 
# Conversely, os.getenv only returns raw strings and fails silently at runtime. It also centralizes configuration, provides IDE autocomplete, and handles .env files natively.

class Settings(BaseSettings):
    llm_api_key: str 
    llm_model: str = "gemini-3.6-flash"
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()