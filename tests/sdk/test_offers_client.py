from unittest.mock import AsyncMock, MagicMock, patch, ANY

import pytest

from sdk.client import OffersClient, BACKEND_MAPPING
from sdk.plugins.interfaces import RequestPlugin, ResponsePlugin
from sdk.utils.exceptions import SDKConfigError


@pytest.fixture
def dummy_plugin():
    class DummyPlugin(RequestPlugin, ResponsePlugin):
        def process_request(self, request):
            return request

        def process_response(self, response):
            return response

    return DummyPlugin()


@patch("sdk.client.ProductsAPI")
@patch("sdk.client.OffersAPI")
@patch("sdk.auth.client.AuthClient")
def test_offers_client_initialization(
    mock_auth_cls,
    mock_offers_api_cls,
    mock_products_api_cls,
):

    mock_auth_instance = MagicMock()
    mock_http_backend_instance = MagicMock()
    mock_products_instance = MagicMock()
    mock_offers_instance = MagicMock()

    mock_auth_cls.return_value = mock_auth_instance
    mock_products_api_cls.return_value = mock_products_instance
    mock_offers_api_cls.return_value = mock_offers_instance

    BACKEND_MAPPING["httpx"] = MagicMock(return_value=mock_http_backend_instance)

    OffersClient(
        base_url="https://api.example.com",
        refresh_token="tok",
        backend_name="httpx",
        cache_ttl_seconds=60,
        request_hooks=None,
        auth_client_factory=mock_auth_cls,
    )

    mock_auth_cls.assert_called_once_with(
        refresh_token="tok",
        base_url="https://api.example.com",
    )

    BACKEND_MAPPING["httpx"].assert_called_once_with(
        auth_client=mock_auth_instance,
        request_hooks=ANY,
    )

    mock_products_api_cls.assert_called_once_with(
        mock_http_backend_instance, "https://api.example.com"
    )

    mock_offers_api_cls.assert_called_once_with(
        mock_http_backend_instance, "https://api.example.com", cache_ttl_seconds=60
    )


@pytest.mark.asyncio
async def test_offers_client_with_aiohttp_backend():
    mock_backend = MagicMock()
    mock_auth = MagicMock()
    
    # Временно переопределяем BACKEND_MAPPING
    original_backend = BACKEND_MAPPING["aiohttp"]
    BACKEND_MAPPING["aiohttp"] = mock_backend

    try:
        client = OffersClient(
            base_url="https://api",
            refresh_token="tok",
            backend_name="aiohttp",
            cache_ttl_seconds=60,
            auth_client_factory=lambda *args, **kwargs: mock_auth,
        )

        mock_backend.assert_called_once_with(
            auth_client=mock_auth,
            request_hooks=[],
        )
        assert client._http_backend is mock_backend.return_value

    finally:
        BACKEND_MAPPING["aiohttp"] = original_backend


@patch("sdk.client.SDKConfig")
def test_offers_client_invalid_backend(mock_config):
    mock_config.return_value.api_base_url = "https://api"
    mock_config.return_value.refresh_token = "tok"
    mock_config.return_value.backend = "invalid"
    mock_config.return_value.ttl_seconds = 60

    with pytest.raises(ValueError, match="Unsupported backend: invalid"):
        OffersClient()


@patch("sdk.client.SDKConfig", side_effect=SDKConfigError("fail"))
def test_offers_client_sdkconfig_error(mock_config):
    with pytest.raises(ValueError, match="Failed to initialize SDK configuration"):
        OffersClient()


@patch("sdk.client.SDKConfig")
@patch("sdk.client.AuthClient")
@patch("sdk.client.HttpxBackend")
@patch("sdk.client.ProductsAPI")
@patch("sdk.client.OffersAPI")
def test_plugin_registration(
    mock_offers_api, mock_products_api,
    mock_httpx_backend, mock_auth, mock_config,
):
    mock_config.return_value.api_base_url = "https://api"
    mock_config.return_value.refresh_token = "tok"
    mock_config.return_value.backend = "httpx"
    mock_config.return_value.ttl_seconds = 60

    mock_product_instance = MagicMock()
    mock_offer_instance = MagicMock()
    mock_products_api.return_value = mock_product_instance
    mock_offers_api.return_value = mock_offer_instance

    OffersClient(plugins=[MagicMock()])

    mock_product_instance.set_plugins.assert_called_once()
    mock_offer_instance.set_plugins.assert_called_once()


@pytest.mark.parametrize("plugin_list, expected_call_count", [
    ([], 0),
    ([MagicMock()], 1),
])
@patch("sdk.client.ProductsAPI")
@patch("sdk.client.OffersAPI")
@patch("sdk.client.HttpxBackend")
@patch("sdk.client.AuthClient")
@patch("sdk.client.SDKConfig")
def test_plugins_applied_correctly(
    mock_config, mock_auth, mock_backend, mock_offers_api, mock_products_api,
    plugin_list, expected_call_count,
):
    mock_config.return_value.api_base_url = "https://api"
    mock_config.return_value.refresh_token = "tok"
    mock_config.return_value.backend = "httpx"
    mock_config.return_value.ttl_seconds = 60

    products_instance = MagicMock()
    offers_instance = MagicMock()
    mock_products_api.return_value = products_instance
    mock_offers_api.return_value = offers_instance

    OffersClient(plugins=plugin_list)

    assert products_instance.set_plugins.call_count == expected_call_count
    assert offers_instance.set_plugins.call_count == expected_call_count


@patch("sdk.client.SDKConfig")
@patch("sdk.client.AuthClient")
@patch("sdk.client.HttpxBackend", new_callable=AsyncMock)
@patch("sdk.client.ProductsAPI")
@patch("sdk.client.OffersAPI")
@pytest.mark.asyncio
async def test_offers_client_context_manager(
    mock_offers_api, mock_products_api,
    mock_backend, mock_auth, mock_config
):
    mock_config.return_value.api_base_url = "https://api"
    mock_config.return_value.refresh_token = "tok"
    mock_config.return_value.backend = "httpx"
    mock_config.return_value.ttl_seconds = 60

    client = OffersClient()
    client._http_backend.aclose = AsyncMock()

    async with client as c:
        assert c is client

    client._http_backend.aclose.assert_awaited_once()
