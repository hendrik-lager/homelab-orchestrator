from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8")

    database_url: str = "sqlite+aiosqlite:///./data/homelab.db"

    secret_key: str

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    alert_from_email: str = ""
    alert_to_emails: list[str] = []

    app_host: str = "127.0.0.1"
    app_port: int = 8000
    log_level: str = "INFO"

    health_check_interval_seconds: int = 60
    update_scan_interval_seconds: int = 3600
    metric_collect_interval_seconds: int = 60

settings = Settings()
