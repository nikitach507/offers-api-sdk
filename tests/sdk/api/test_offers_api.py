import pytest
import time
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from sdk.api.offers import OffersAPI
from sdk.models.offer import Offer
from sdk.utils.exceptions import OffersAPIError


@pytest.fixture
def dummy_offer_data():
    return [{"id": str(uuid4()), "price": 100, 'items_in_stock': 42}]


@pytest.fixture
def dummy_offer_model(dummy_offer_data):
    return [Offer.model_validate(d) for d in dummy_offer_data]


@pytest.mark.asyncio
async def test_returns_cached_offers(monkeypatch, dummy_offer_model):
    product_id = uuid4()
    api = OffersAPI(http_backend=MagicMock(), base_url="https://api.test", cache_ttl_seconds=60)
    api._cache[product_id] = (dummy_offer_model, time.time())

    result = await api.get_offers(product_id)
    assert result == dummy_offer_model


@pytest.mark.asyncio
async def test_fetches_new_offers_when_cache_expired(dummy_offer_data):
    product_id = uuid4()
    backend = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value=dummy_offer_data)
    backend.request = AsyncMock(return_value=mock_response)

    api = OffersAPI(http_backend=backend, base_url="https://api.test", cache_ttl_seconds=0)
    api._cache[product_id] = ([Offer.model_validate(d) for d in dummy_offer_data], time.time() - 100)

    result = await api.get_offers(product_id)
    assert isinstance(result, list)
    assert isinstance(result[0], Offer)
    assert backend.request.called


@pytest.mark.asyncio
async def test_fetches_offers_when_not_cached(dummy_offer_data):
    product_id = uuid4()
    backend = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value=dummy_offer_data)
    backend.request = AsyncMock(return_value=mock_response)

    api = OffersAPI(http_backend=backend, base_url="https://api.test")

    result = await api.get_offers(product_id)
    assert isinstance(result, list)
    assert isinstance(result[0], Offer)
    assert product_id in api._cache


@pytest.mark.asyncio
async def test_raises_if_invalid_response_data():
    product_id = uuid4()
    backend = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value=[{"bad": "data"}])
    backend.request = AsyncMock(return_value=mock_response)

    api = OffersAPI(http_backend=backend, base_url="https://api.test")

    with pytest.raises(OffersAPIError, match="Invalid offer data"):
        await api.get_offers(product_id)
