import json
import pytest
from unittest.mock import AsyncMock, patch
from sdk.http.backends.httpx_backend import HttpxBackend, HttpxResponseAdapter
from sdk.utils.exceptions import RequestExecutionError
import httpx

from sdk.auth.client import AuthClient


@pytest.fixture
def auth_client():
    mock = AsyncMock(spec=AuthClient)
    mock.get_access_token = AsyncMock(return_value="access-token")
    return mock


@pytest.mark.asyncio
async def test_httpx_backend_success(auth_client):
    backend = HttpxBackend(auth_client)

    with patch.object(backend._httpx_client, "request", new=AsyncMock()) as mock_request:
        mock_request.return_value = httpx.Response(200, text="OK")

        resp = await backend.request("GET", "https://example.com")
        assert resp.status_code == 200
        assert resp.text == "OK"

    await backend.aclose()


@pytest.mark.asyncio
async def test_token_is_injected_in_headers(auth_client):
    backend = HttpxBackend(auth_client)
    captured_headers = {}

    async def mock_httpx_request(method, url, **kwargs):
        nonlocal captured_headers
        captured_headers = kwargs.get("headers", {})
        return httpx.Response(200)

    with patch.object(backend._httpx_client, "request", new=mock_httpx_request):
        await backend.request("GET", "https://example.com", headers={})

    assert "Bearer" in captured_headers
    assert captured_headers["Bearer"] == "access-token"

    await backend.aclose()


@pytest.mark.asyncio
async def test_httpx_backend_request_error(auth_client):
    backend = HttpxBackend(auth_client)

    with patch.object(backend._httpx_client, "request", new=AsyncMock(side_effect=httpx.RequestError("fail"))):
        with pytest.raises(RequestExecutionError, match="HTTPX request failed"):
            await backend.request("GET", "https://example.com")

    await backend.aclose()


@pytest.mark.asyncio
async def test_response_adapter():
    data = {"ok": True}
    content = json.dumps(data).encode("utf-8")

    response = httpx.Response(
        status_code=201,
        content=content,
        headers={"Content-Type": "application/json"},
    )

    adapter = HttpxResponseAdapter(response)

    assert adapter.status_code == 201
    assert adapter.text == content.decode("utf-8")

    json_data = await adapter.json()
    assert json_data == data
