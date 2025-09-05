from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	app_name: str = "FastAPI CRUD"
	secret_key: str = "CHANGE_THIS"  # Default fallback value

	model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
