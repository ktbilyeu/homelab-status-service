from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Dict


def parse_service_enabled(value):
    if isinstance(value, str) and value.lower() in ("true", "false"):
        value = value.lower() == "true"
    if not isinstance(value, bool):
        raise ValueError("Service enabled must be a boolean or true/false string")
    return value


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./status.db"
    API_PREFIX: str = "/api"
    CHECK_INTERVAL: int = 60
    TIMEOUT: int = 10

    CORS_ORIGINS: List[str] = [
        "https://kadenbilyeu.com",
        "https://status.kadenbilyeu.com",
        "https://kakusui.org",
        "https://status.kakusui.org",
        "https://easytl.org",
        "https://status.easytl.org",
        "https://tetragroup.io",
        "https://status.tetragroup.io",
        "http://localhost:5173",
        "https://kadenbilyeu-com.pages.dev",
    ]
    CORS_ALLOW_ORIGIN_REGEX: str = r"^https://([a-z0-9-]+\.)?(kadenbilyeu-com\.pages\.dev|kadenbilyeu\.com|kakusui\.org|easytl\.org|tetragroup\.io)$"

    SERVICES: List[Dict[str, str | bool]] = [
        {
            "name": "Personal Website (kadenbilyeu.com)",
            "url": "https://kadenbilyeu.com",
            "check_type": "http",
            "expected_status": "200",
            "domains": "kadenbilyeu.com"
        },
        {
            "name": "Personal Website API (api.kadenbilyeu.com)",
            "url": "https://api.kadenbilyeu.com",
            "check_type": "http",
            "expected_status": "200",
            "domains": "kadenbilyeu.com"
        },
        {
            "name": "Git (git.kadenbilyeu.com)",
            "url": "https://git.kadenbilyeu.com",
            "check_type": "http",
            "expected_status": "200",
            "domains": "kadenbilyeu.com"
        },
        {
            "name": "Kakusui API (api.kakusui.org)",
            "url": "https://api.kakusui.org",
            "enabled": False,
            "check_type": "http",
            "expected_status": "200",
            "domains": "kadenbilyeu.com,kakusui.org,easytl.org"
        },
        {
            "name": "EasyTL Website (easytl.org)",
            "url": "https://easytl.org",
            "check_type": "http",
            "expected_status": "200",
            "domains": "kadenbilyeu.com,easytl.org"
        },
        {
            "name": "TetraGroup Website (tetragroup.io)",
            "url": "https://tetragroup.io",
            "check_type": "http",
            "expected_status": "200",
            "domains": "kadenbilyeu.com,tetragroup.io"
        },
        {
            "name": "Momentum (momentum.kadenbilyeu.com)",
            "url": "https://momentum.kadenbilyeu.com",
            "check_type": "http",
            "expected_status": "200",
            "domains": "kadenbilyeu.com"
        },
    ]

    @field_validator("SERVICES")
    @classmethod
    def validate_enabled_flags(cls, services):
        for service in services:
            if "enabled" not in service:
                continue
            service["enabled"] = parse_service_enabled(service["enabled"])
        return services

    class Config:
        env_file = ".env"
        case_sensitive = False
        # A private deployment file may also contain Compose-only settings.
        extra = "ignore"

settings = Settings()
