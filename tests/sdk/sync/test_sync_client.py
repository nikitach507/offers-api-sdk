import asyncio
from uuid import uuid4

from unittest.mock import AsyncMock, patch, MagicMock
from sdk.sync.client import SyncOffersClient
from sdk.sync.client import SyncOffersAPI


def test_sync_offers_client_lifecycle():
    mock_products_api = AsyncMock()
    mock_offers_api = AsyncMock()

    mock_client_instance = MagicMock()
    mock_client_instance.products = mock_products_api
    mock_client_instance.offers = mock_offers_api
    mock_client_instance.aclose = AsyncMock()

    with patch("sdk.sync.client.OffersClient", return_value=mock_client_instance) as mock_offers_client_cls:
        client = SyncOffersClient(base_url="https://api.example.com", refresh_token="dummy", backend="httpx")

        assert client.products._products_api is mock_products_api
        assert client.offers._offers_api is mock_offers_api

        client.close()
        mock_client_instance.aclose.assert_awaited_once()

        mock_offers_client_cls.assert_called_once_with(
            base_url="https://api.example.com",
            refresh_token="dummy",
            backend="httpx"
        )


def test_sync_get_offers():
    loop = asyncio.new_event_loop()
    offers_api = AsyncMock()
    offers_api.get_offers.return_value = [{"id": "123", "price": 100}]

    api = SyncOffersAPI(offers_api=offers_api, event_loop=loop)
    result = api.get_offers(uuid4())

    assert result == [{"id": "123", "price": 100}]
    offers_api.get_offers.assert_called_once()
