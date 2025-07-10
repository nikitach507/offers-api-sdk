import pytest
from unittest.mock import AsyncMock

from sdk.api.constatns import HTTPMethod
from sdk.api.products import ProductsAPI
from sdk.utils.exceptions import OffersAPIError
from sdk.http.interfaces import HTTPBackend


@pytest.fixture
def dummy_product_data():
    return {
        "id": "1c7d3c56-74cb-4260-9910-3f6cc8c0c123",
        "name": "Test Product",
        "description": "This is a test product"
    }


@pytest.fixture
def dummy_response():
    return {
        "id": "1c7d3c56-74cb-4260-9910-3f6cc8c0c123",
        "name": "Test Product",
        "description": "This is a test product",
        "registered": True
    }


@pytest.fixture
def mock_backend():
    backend = AsyncMock(spec=HTTPBackend)
    return backend


@pytest.mark.asyncio
async def test_register_product_success(mock_backend, dummy_product_data, dummy_response):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = dummy_response
    mock_backend.request.return_value = mock_response

    api = ProductsAPI(http_backend=mock_backend, base_url="https://api.example.com")
    result = await api.register_product(dummy_product_data)

    assert result == dummy_response

    mock_backend.request.assert_awaited_once()
    args, kwargs = mock_backend.request.await_args

    assert args[0] == HTTPMethod.POST
    assert args[1] == "https://api.example.com/api/v1/products/register"

    assert kwargs["json"] == dummy_product_data


@pytest.mark.asyncio
async def test_register_product_invalid_json(mock_backend, dummy_product_data):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_backend.request.return_value = mock_response

    api = ProductsAPI(http_backend=mock_backend, base_url="https://api.example.com")

    with pytest.raises(OffersAPIError) as exc:
        await api.register_product(dummy_product_data)

    assert "Invalid JSON in register_product response" in str(exc.value)


@pytest.mark.asyncio
async def test_register_products_mixed_results(mock_backend, dummy_product_data, dummy_response):
    success_response = AsyncMock()
    success_response.status_code = 200
    success_response.json.return_value = dummy_response

    fail_response = AsyncMock()
    fail_response.status_code = 500
    fail_response.json.side_effect = ValueError("Server error")

    mock_backend.request.side_effect = [
        success_response,
        fail_response,
        Exception("Unexpected")
    ]

    api = ProductsAPI(http_backend=mock_backend, base_url="https://api.example.com")

    results = await api.register_products([
        dummy_product_data,
        dummy_product_data,
        dummy_product_data
    ])

    assert len(results) == 1
    assert results[0] == dummy_response
