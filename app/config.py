from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    gemini_api_key: str
    groq_api_key: str
    openrouter_api_key: str
    mistral_api_key: str

settings = Settings()
