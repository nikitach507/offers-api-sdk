import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from requests import Response as RequestsResponse, RequestException
from sdk.http.backends.requests_backend import RequestsBackend, RequestsResponseAdapter
from sdk.utils.exceptions import OffersAPIError, RequestExecutionError


@pytest.fixture
def auth_client():
    mock = AsyncMock()
    mock.get_access_token = AsyncMock(return_value="valid-token")
    return mock


def make_fake_response(status_code=200, text="OK"):
    response = MagicMock(spec=RequestsResponse)
    response.status_code = status_code
    response.text = text
    response.json.return_value = {"ok": True}
    return response


@pytest.mark.asyncio
async def test_requests_backend_success(auth_client):
    backend = RequestsBackend(auth_client)

    with patch.object(backend._session, "request", return_value=make_fake_response()) as mock_req:
        resp = await backend.request("GET", "https://example.com")

        assert resp.status_code == 200
        assert resp.text == "OK"
        assert await resp.json() == {"ok": True}

        mock_req.assert_called_once()
        headers = mock_req.call_args.kwargs["headers"]
        assert headers["Bearer"] == "valid-token"


@pytest.mark.asyncio
async def test_token_refreshed_on_401(auth_client):
    auth_client.get_access_token = AsyncMock(side_effect=["expired-token", "refreshed-token"])

    backend = RequestsBackend(auth_client)

    def side_effect(*args, **kwargs):
        token = kwargs["headers"]["Bearer"]
        if token == "expired-token":
            return make_fake_response(401, "Access token expired")
        return make_fake_response(200, "Success")

    with patch.object(backend._session, "request", side_effect=side_effect) as mock_req:
        resp = await backend.request("GET", "https://example.com")
        assert resp.status_code == 200
        assert resp.text == "Success"

        assert mock_req.call_count == 2


@pytest.mark.asyncio
async def test_hook_failure_raises(auth_client):
    async def bad_hook(method, url, kwargs):
        raise ValueError("Hook failed")

    backend = RequestsBackend(auth_client, request_hooks=[bad_hook])

    with pytest.raises(OffersAPIError, match="Request hook"):
        await backend.request("GET", "https://example.com")


@pytest.mark.asyncio
async def test_request_exception_wrapped(auth_client):
    backend = RequestsBackend(auth_client)

    with patch.object(backend._session, "request", side_effect=RequestException("boom")):
        with pytest.raises(RequestExecutionError, match="Network error"):
            await backend.request("GET", "https://example.com")


@pytest.mark.asyncio
async def test_response_adapter():
    mock_response = make_fake_response(201, '{"hello": "world"}')
    adapter = RequestsResponseAdapter(mock_response)

    assert adapter.status_code == 201
    assert adapter.text == '{"hello": "world"}'
    json_data = await adapter.json()
    assert json_data == {"ok": True}
