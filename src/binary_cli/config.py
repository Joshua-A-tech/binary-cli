import os
from pathlib import Path

from dotenv import load_dotenv
from platformdirs import user_config_dir, user_data_dir
from pydantic import BaseModel, Field


class Settings(BaseModel):
    provider: str = Field(default="ollama")
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"

    @property
    def model(self) -> str:
        if self.provider == "openai":
            return self.openai_model
        if self.provider == "gemini":
            return self.gemini_model
        return self.ollama_model


def load_settings(validate_keys: bool = True) -> Settings:
    load_dotenv()
    values = {
        "provider": os.getenv("BINARY_PROVIDER", "ollama").lower(),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openai_model": os.getenv("BINARY_OPENAI_MODEL", "gpt-4o-mini"),
        "ollama_base_url": os.getenv("BINARY_OLLAMA_BASE_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("BINARY_OLLAMA_MODEL", "llama3.2"),
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "gemini_model": os.getenv("BINARY_GEMINI_MODEL", "gemini-1.5-flash"),
    }
    settings = Settings(**values)
    valid_providers = {"openai", "ollama", "gemini"}
    if settings.provider not in valid_providers:
        raise ValueError(f"BINARY_PROVIDER must be one of: {', '.join(sorted(valid_providers))}.")
    if validate_keys:
        if settings.provider == "openai" and not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when BINARY_PROVIDER=openai.")
        if settings.provider == "gemini" and not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when BINARY_PROVIDER=gemini.")
    return settings


def data_directory() -> Path:
    path = Path(user_data_dir("binary-cli"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def config_directory() -> Path:
    path = Path(user_config_dir("binary-cli"))
    path.mkdir(parents=True, exist_ok=True)
    return path
