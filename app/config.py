from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Platform Auth
    database_url: str
    master_api_key: str

    # Provider API keys
    gemini_api_key: str
    groq_api_key: str
    openrouter_api_key: str
    mistral_api_key: str

    #  Tools API keys
    alpha_vantage_api_key: str
    openweathermap_api_key: str
    news_api_key: str
    google_search_api_key: str
    google_cse_id: str

    pinecone_api_key: str

settings = Settings()
