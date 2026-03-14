from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = ""

    # Google OAuth2
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "sqlite+aiosqlite:///./data/cass.db"

    # Sandboxed file access
    allowed_directories: str = "~/Documents,~/Downloads"

    # Assistant
    assistant_name: str = "Cass"

    @property
    def allowed_dirs(self) -> list[Path]:
        return [Path(d.strip()).expanduser().resolve() for d in self.allowed_directories.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
