import pytest
import json
import re
from pydantic_settings import SettingsError
from pydantic import ValidationError
from config import Settings

def test_default_config():
    settings = Settings()

    assert settings.DATABASE_URL == "sqlite+aiosqlite:///./status.db"
    assert settings.API_PREFIX == "/api"
    assert settings.CHECK_INTERVAL == 60
    assert settings.TIMEOUT == 10

def test_services_configured():
    settings = Settings()

    assert len(settings.SERVICES) > 0
    assert all("name" in s for s in settings.SERVICES)
    assert all("url" in s for s in settings.SERVICES)
    assert all("check_type" in s for s in settings.SERVICES)
    assert all("expected_status" in s for s in settings.SERVICES)

def test_service_urls_valid():
    settings = Settings()

    for service in settings.SERVICES:
        assert service["url"].startswith("http://") or service["url"].startswith("https://")

def test_check_interval_positive():
    settings = Settings()
    assert settings.CHECK_INTERVAL > 0

def test_timeout_positive():
    settings = Settings()
    assert settings.TIMEOUT > 0

def test_private_service_and_cors_environment(monkeypatch):
    services = [{
        "name": "Legacy service",
        "url": "https://legacy.example.test",
        "check_type": "http",
        "expected_status": "200",
        "domains": "example.test,legacy.example.test",
    }]
    origins = ["https://legacy.example.test"]
    pattern = r"^https://([a-z0-9-]+\.)?legacy\.example\.test$"
    monkeypatch.setenv("SERVICES", json.dumps(services))
    monkeypatch.setenv("CORS_ORIGINS", json.dumps(origins))
    monkeypatch.setenv("CORS_ALLOW_ORIGIN_REGEX", pattern)

    settings = Settings(_env_file=None)

    assert settings.SERVICES == services
    assert settings.CORS_ORIGINS == origins
    assert re.fullmatch(settings.CORS_ALLOW_ORIGIN_REGEX, "https://preview.legacy.example.test")
    assert not re.fullmatch(settings.CORS_ALLOW_ORIGIN_REGEX, "https://legacy.example.test.attacker.test")

def test_shared_private_dotenv_accepts_compose_settings(tmp_path):
    private_env = tmp_path / "runtime.env"
    private_env.write_text(
        "CORS_ORIGINS='[\"https://legacy.example.test\"]'\n"
        "CORS_ALLOW_ORIGIN_REGEX='^https://legacy\\.example\\.test$'\n"
        "STATUS_ROUTER_RULE='Host(`status.legacy.example.test`)'\n",
        encoding="utf-8",
    )

    settings = Settings(_env_file=private_env)

    assert settings.CORS_ORIGINS == ["https://legacy.example.test"]
    assert re.fullmatch(settings.CORS_ALLOW_ORIGIN_REGEX, "https://legacy.example.test")

@pytest.mark.parametrize("key", ["SERVICES", "CORS_ORIGINS"])
def test_invalid_private_json_fails_instead_of_using_defaults(monkeypatch, key):
    monkeypatch.setenv(key, "not-json")

    with pytest.raises(SettingsError):
        Settings(_env_file=None)

@pytest.mark.parametrize("disabled", [False, "false", "FALSE"])
def test_service_retirement_accepts_boolean_and_legacy_string(disabled):
    service = {"name": "Legacy service", "url": "https://legacy.example.test", "enabled": disabled}
    assert Settings(_env_file=None, SERVICES=[service]).SERVICES[0]["enabled"] is False
    with pytest.raises(ValidationError, match="boolean"):
        Settings(_env_file=None, SERVICES=[{**service, "enabled": "sometimes"}])
