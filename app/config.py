from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_secret: str = "change-me"
    local_auth_token: str = "local-token"

    database_url: str = "sqlite+pysqlite:///./bughunt.db"
    evidence_dir: str = "/data/evidence"
    reports_dir: str = "/data/reports"
    log_dir: str = "/data/logs"
    backup_dir: str = "/data/backups"

    research_mode: str = "passive"
    approval_mode: str = "human_required"
    auto_report_submission: bool = False
    allow_destructive_testing: bool = False
    default_rate_limit_rps: int = 1
    max_campaign_duration_minutes: int = 60
    max_total_requests: int = 200
    max_workers: int = 1

    model_provider: str = "mock"
    model_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        protected_namespaces=("settings_",),
    )


settings = Settings()
