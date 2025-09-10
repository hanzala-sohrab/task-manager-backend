from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI CRUD"
    secret_key: str = "CHANGE_THIS"  # Default fallback value

    # Ollama settings
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout: int = 30

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
