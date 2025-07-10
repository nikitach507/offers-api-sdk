import time
import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from sdk.auth.client import AuthClient
from sdk.utils.exceptions import AuthRequestError


@pytest.mark.asyncio
async def test_returns_cached_token_if_valid():
    client = AuthClient(refresh_token="r1", base_url="https://api.test")
    client._access_token = "cached-token"
    client._token_expiry_timestamp = time.time() + 3600  # valid

    token = await client.get_access_token()
    assert token == "cached-token"


@pytest.mark.asyncio
async def test_requests_new_token_if_expired():
    client = AuthClient(refresh_token="r1", base_url="https://api.test")
    client._access_token = "old"
    client._token_expiry_timestamp = time.time() - 100

    with patch.object(client, "_request_new_token", new=AsyncMock(return_value="new-token")):
        token = await client.get_access_token()
        assert token == "new-token"
        assert client._access_token == "new-token"


@pytest.mark.asyncio
async def test_forces_refresh_even_if_token_valid():
    client = AuthClient(refresh_token="r1", base_url="https://api.test")
    client._access_token = "old-token"
    client._token_expiry_timestamp = time.time() + 1000

    with patch.object(client, "_request_new_token", new=AsyncMock(return_value="forced-token")):
        token = await client.get_access_token(force_refresh=True)
        assert token == "forced-token"


@pytest.mark.asyncio
async def test_raises_if_no_refresh_token():
    client = AuthClient(refresh_token=None, base_url="https://api.test")
    with pytest.raises(AuthRequestError, match="Refresh token is not set"):
        await client.get_access_token()


@pytest.mark.asyncio
async def test_request_token_success():
    client = AuthClient(refresh_token="r1", base_url="https://api.test")

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "new-token"}

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_response)):
        token = await client._request_new_token("r1")
        assert token == "new-token"


@pytest.mark.asyncio
async def test_request_token_http_error():
    client = AuthClient(refresh_token="r1", base_url="https://api.test")
    error = httpx.HTTPStatusError("error", request=MagicMock(),
                                  response=MagicMock(status_code=401, text="Unauthorized"))

    with patch("httpx.AsyncClient.post", new=AsyncMock(side_effect=error)):
        with pytest.raises(AuthRequestError, match="Authentication failed with status code"):
            await client._request_new_token("r1")


@pytest.mark.asyncio
async def test_request_token_network_error():
    client = AuthClient(refresh_token="r1", base_url="https://api.test")
    error = httpx.RequestError("boom", request=MagicMock())

    with patch("httpx.AsyncClient.post", new=AsyncMock(side_effect=error)):
        with pytest.raises(AuthRequestError, match="Network error during authentication"):
            await client._request_new_token("r1")


@pytest.mark.asyncio
async def test_request_token_invalid_json():
    client = AuthClient(refresh_token="r1", base_url="https://api.test")

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("not JSON")

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_response)):
        with pytest.raises(AuthRequestError, match="Invalid response structure"):
            await client._request_new_token("r1")
