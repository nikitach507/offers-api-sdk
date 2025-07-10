import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from aiohttp import ClientResponse, ContentTypeError
from sdk.http.backends.aiohttp_backend import AioHttpBackend, AioHttpResponseAdapter
from sdk.auth.client import AuthClient


@pytest.fixture
def auth_client():
    mock = AsyncMock(spec=AuthClient)
    mock.get_access_token = AsyncMock(return_value="access-token")
    return mock


@pytest.mark.asyncio
async def test_aiohttp_backend_success(auth_client):
    backend = AioHttpBackend(auth_client)

    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="OK")
    mock_response.json = AsyncMock(return_value={"ok": True})

    class MockContextManager:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch.object(backend._client_session, "request", return_value=MockContextManager()):
        response = await backend.request("GET", "https://example.com")

        assert response.status_code == 200
        assert response.text == "OK"
        assert await response.json() == {"ok": True}

    await backend.aclose()


@pytest.mark.asyncio
async def test_aiohttp_token_is_injected(auth_client):
    auth_client.get_access_token = AsyncMock(return_value="access-token")
    backend = AioHttpBackend(auth_client)

    headers_captured = {}

    class MockResponseContextManager:
        async def __aenter__(self):
            mock_resp = MagicMock(spec=ClientResponse)
            mock_resp.status = 200
            mock_resp.text = AsyncMock(return_value="OK")
            mock_resp.json = AsyncMock(return_value={"ok": True})
            return mock_resp

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    def mock_request(method, url, headers=None, **kwargs):
        nonlocal headers_captured
        headers_captured = headers or {}
        return MockResponseContextManager()

    with patch.object(backend._client_session, "request", new=mock_request):
        await backend.request("GET", "https://example.com", headers={"X-Test": "1"})

    assert headers_captured["Bearer"] == "access-token"
    assert headers_captured["X-Test"] == "1"

    await backend.aclose()


@pytest.mark.asyncio
async def test_aiohttp_backend_json_parse_failure(auth_client):
    auth_client.get_access_token = AsyncMock(return_value="access-token")
    backend = AioHttpBackend(auth_client)

    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="Not a JSON")
    mock_response.json = AsyncMock(side_effect=ContentTypeError(
        request_info=None, history=None, message="Invalid"
    ))

    class MockContextManager:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    def mock_request(*args, **kwargs):
        return MockContextManager()

    with patch.object(backend._client_session, "request", new=mock_request):
        resp = await backend.request("GET", "https://example.com", headers={})
        assert resp.status_code == 200
        assert resp.text == "Not a JSON"
        assert await resp.json() is None

    await backend.aclose()


@pytest.mark.asyncio
async def test_aiohttp_response_adapter():
    mock_response = MagicMock(spec=ClientResponse)
    mock_response.status = 201
    body = '{"key":"value"}'

    adapter = AioHttpResponseAdapter(mock_response, body, {"key": "value"})
    assert adapter.status_code == 201
    assert adapter.text == body
    assert await adapter.json() == {"key": "value"}


@pytest.mark.asyncio
async def test_aiohttp_aclose_closes_session(auth_client):
    backend = AioHttpBackend(auth_client)
    with patch.object(backend._client_session, "close", new=AsyncMock()) as close_mock:
        await backend.aclose()
        close_mock.assert_awaited_once()
