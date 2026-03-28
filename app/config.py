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

    # Pinecone Configs
    pinecone_namespace: str
    pinecone_index_name: str
    pinecone_api_key: str
    gemini_embedding_model: str = "gemini-embedding-001"

    # Base URLs
    alpha_vantage_base_url: str = "https://www.alphavantage.co/query"
    crypto_base_url: str = "https://api.coingecko.com/api/v3"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    mistral_base_url: str = "https://api.mistral.ai/v1"
    news_base_url: str = "https://newsapi.org/v2/everything"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    wandbox_base_url: str = "https://wandbox.org/api/compile.json"
    weather_base_url: str = "https://api.openweathermap.org/data/2.5/weather"
    wikipedia_base_url: str = "https://en.wikipedia.org/w/api.php"

settings = Settings()
