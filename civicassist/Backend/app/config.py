from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "CivicAssist AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"

    MAPBOX_ACCESS_TOKEN: str = ""

    # Kept for compatibility with older code/config files.
    LLM_PROVIDER: str = "gemini"

    DATABASE_URL: str = "sqlite:///./civicassist.db"

    TAVILY_PROVIDER: str = "tavily"
    TAVILY_API_KEY: str = "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"


    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    VECTOR_DB_DIR: str = "vector_db"
    VECTOR_COLLECTION_NAME: str = "civicassist"

    MYSCHEME_URL: str = "https://www.myscheme.gov.in/"
    DATA_GOV_URL: str = "https://www.data.gov.in/"
    INDIA_CODE_URL: str = "https://www.indiacode.nic.in/"

    SECRET_KEY: str = "change-this-to-a-random-secret-key"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def upload_path(self) -> Path:
        path = Path(self.UPLOAD_DIR)

        if not path.is_absolute():
            path = BASE_DIR / path

        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def vector_db_path(self) -> Path:
        path = Path(self.VECTOR_DB_DIR)

        if not path.is_absolute():
            path = BASE_DIR / path

        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()