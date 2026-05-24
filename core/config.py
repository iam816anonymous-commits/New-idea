from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "PropPulse OS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./proppulse.db"

    # Mock Config
    WHATSAPP_SIMULATION_DELAY: float = 1.5

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
