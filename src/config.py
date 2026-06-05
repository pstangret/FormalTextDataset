import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

# Obliczamy absolutną ścieżkę do głównego folderu projektu (FormalTextDataset)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Centralna konfiguracja ładowana automatycznie z pliku .env"""
    groq_api_keys: str = Field(default="", alias="GROQ_API_KEYS")
    google_api_keys: str = Field(default="", alias="GOOGLE_API_KEYS")

    chunk_size: int = Field(default=300, alias="TARGET_CHUNK_SIZE")
    wiki_limit: int = Field(default=50, alias="WIKI_ARTICLES_LIMIT")
    lektury_limit: int = Field(default=20, alias="LEKTURY_BOOKS_LIMIT")

    # Ścieżki systemowe
    base_dir: Path = BASE_DIR
    data_dir: Path = Field(default_factory=lambda: BASE_DIR / "data")

    model_config = {
        # Wymuszamy czytanie z dokładnej ścieżki absolutnej do pliku .env
        "env_file": str(BASE_DIR / ".env"),
        "extra": "ignore"
    }

    def ensure_dirs(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)


# Singleton konfiguracji gotowy do importu
settings = Settings()
settings.ensure_dirs()