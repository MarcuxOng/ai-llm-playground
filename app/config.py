from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    gemini_api_key: str
    gemini_model: str

    groq_api_key: str
    groq_model: str

    openrouter_url: str
    openrouter_api_key: str
    openrouter_model: str

    mistral_api_key: str
    mistral_model: str

    bytez_api_key: str
    bytez_model: str

settings = Settings()
