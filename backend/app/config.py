from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Banco
    database_url: str = "postgresql://revit_ai:revit_ai@localhost:5432/revit_ai"

    # LLM
    llm_provider: str = "anthropic"  # "anthropic" | "openai"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Embeddings
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384

    # Revit bridge (add-in C#)
    revit_bridge_url: str = "http://host.docker.internal:5005"
    revit_bridge_timeout: float = 15.0


settings = Settings()
