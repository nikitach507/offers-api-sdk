import pytest
import yaml
from sdk.config.sdk_config import SDKConfig
from sdk.utils.exceptions import SDKConfigError


def test_config_uses_direct_arguments(monkeypatch):
    monkeypatch.delenv("API_BASE_URL", raising=False)
    monkeypatch.delenv("REFRESH_TOKEN", raising=False)

    config = SDKConfig(
        api_base_url="https://direct.url",
        refresh_token="direct_token",
        backend="httpx",
        ttl_seconds=123
    )

    assert config.api_base_url == "https://direct.url"
    assert config.refresh_token == "direct_token"
    assert config.backend == "httpx"
    assert config.ttl_seconds == 123


def test_config_falls_back_to_env(monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "https://env.url")
    monkeypatch.setenv("REFRESH_TOKEN", "env_token")
    monkeypatch.setenv("BACKEND", "aiohttp")
    monkeypatch.setenv("TTL_SECONDS", "999")

    config = SDKConfig()

    assert config.api_base_url == "https://env.url"
    assert config.refresh_token == "env_token"
    assert config.backend == "aiohttp"
    assert config.ttl_seconds == 999


def test_config_falls_back_to_yaml(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_data = {
        "api_base_url": "https://yaml.url",
        "refresh_token": "yaml_token",
        "backend": "requests",
        "ttl_seconds": 321
    }
    config_path.write_text(yaml.safe_dump(config_data))

    monkeypatch.delenv("API_BASE_URL", raising=False)
    monkeypatch.delenv("REFRESH_TOKEN", raising=False)
    monkeypatch.delenv("BACKEND", raising=False)
    monkeypatch.delenv("TTL_SECONDS", raising=False)

    config = SDKConfig(config_path=str(config_path))

    assert config.api_base_url == "https://yaml.url"
    assert config.refresh_token == "yaml_token"
    assert config.backend == "requests"
    assert config.ttl_seconds == 321


def test_config_raises_on_missing_required(monkeypatch):
    monkeypatch.delenv("API_BASE_URL", raising=False)
    monkeypatch.delenv("REFRESH_TOKEN", raising=False)

    with pytest.raises(SDKConfigError, match="API base URL must be set"):
        SDKConfig(refresh_token="x", api_base_url=None)

    with pytest.raises(SDKConfigError, match="Refresh token must be set"):
        SDKConfig(api_base_url="https://x", refresh_token=None)


def test_config_raises_on_invalid_backend(monkeypatch):
    monkeypatch.delenv("BACKEND", raising=False)
    with pytest.raises(SDKConfigError, match="Invalid backend: invalid"):
        SDKConfig(api_base_url="https://x", refresh_token="y", backend="invalid")
