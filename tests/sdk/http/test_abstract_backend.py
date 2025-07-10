import pytest
from unittest.mock import AsyncMock
from sdk.http.backends.base_async_backend import AbstractAsyncBackend
from sdk.utils.exceptions import OffersAPIError, RequestExecutionError
from sdk.http.interfaces import BaseResponse


class DummyResponse(BaseResponse):
    def __init__(self, status_code: int, text: str = ""):
        self._status_code = status_code
        self._text = text

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def text(self) -> str:
        return self._text

    async def json(self):
        return {"dummy": True}


class DummyBackend(AbstractAsyncBackend):
    async def request(self, method: str, url: str, **kwargs):
        pass


@pytest.fixture
def auth_client():
    mock = AsyncMock()
    mock.get_access_token = AsyncMock(return_value="valid-token")
    return mock


@pytest.mark.asyncio
async def test_request_with_auth_success(auth_client):
    backend = DummyBackend(auth_client)

    async def request_fn(method: str, url: str, token: str, **kwargs):
        assert method == "GET"
        assert url == "https://example.com"
        assert token == "valid-token"
        return DummyResponse(200, "OK")

    response = await backend._request_with_auth("GET", "https://example.com", execute_request=request_fn)
    assert response.status_code == 200
    assert response.text == "OK"


@pytest.mark.asyncio
async def test_request_with_auth_retry_on_401(auth_client):
    auth_client.get_access_token = AsyncMock(side_effect=["expired-token", "refreshed-token"])

    backend = DummyBackend(auth_client)

    calls = []

    async def request_fn(method: str, url: str, token: str, **kwargs):
        calls.append(token)
        if token == "expired-token":
            return DummyResponse(401, "Access token expired")
        return DummyResponse(200, "Success")

    response = await backend._request_with_auth("GET", "https://example.com", execute_request=request_fn)
    assert response.status_code == 200
    assert calls == ["expired-token", "refreshed-token"]


@pytest.mark.asyncio
async def test_request_with_auth_hook_failure(auth_client):
    async def failing_hook(method, url, kwargs):
        raise ValueError("Boom")

    backend = DummyBackend(auth_client, request_hooks=[failing_hook])

    async def request_fn(token: str, **kwargs):
        return DummyResponse(200, "OK")

    with pytest.raises(OffersAPIError, match="Request hook"):
        await backend._request_with_auth("GET", "https://example.com", execute_request=request_fn)


@pytest.mark.asyncio
async def test_request_with_auth_request_execution_error(auth_client):
    backend = DummyBackend(auth_client)

    async def request_fn(method: str, url: str, token: str, **kwargs):
        raise RequestExecutionError("Network failure")

    with pytest.raises(RequestExecutionError, match="Network failure"):
        await backend._request_with_auth("GET", "https://example.com", execute_request=request_fn)
