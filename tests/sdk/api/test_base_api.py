import pytest
from unittest.mock import AsyncMock

from sdk.api.base_api import BaseAPI
from sdk.api.constatns import HTTPMethod


@pytest.mark.asyncio
async def test_request_with_plugins_and_successful_response():
    http_mock = AsyncMock()
    response_mock = AsyncMock()
    response_mock.status_code = 200
    response_mock.text = "OK"
    http_mock.request.return_value = response_mock

    request_plugin = AsyncMock()
    response_plugin = AsyncMock()

    api = BaseAPI(http_backend=http_mock, base_url="https://api.example.com")
    api.set_plugins([request_plugin], [response_plugin])

    result = await api._request(HTTPMethod.GET, "/test", params={"foo": "bar"})

    # assert full request sent
    http_mock.request.assert_awaited_once_with(
        HTTPMethod.GET, "https://api.example.com/test", params={"foo": "bar"}
    )
    # plugins executed
    request_plugin.process_request.assert_awaited_once()
    response_plugin.process_response.assert_awaited_once_with(response_mock)
    # response returned as is
    assert result == response_mock
