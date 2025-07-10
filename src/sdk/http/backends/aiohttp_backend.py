from typing import Any

from aiohttp import ClientResponse, ClientSession, ClientTimeout, ContentTypeError

from sdk.auth.client import AuthClient
from sdk.http.backends.base_async_backend import AbstractAsyncBackend
from sdk.http.hooks.type import RequestHook
from sdk.http.interfaces import BaseResponse, HTTPBackend


class AioHttpResponseAdapter(BaseResponse):
    def __init__(self, client_response: ClientResponse, response_body: str, parsed_json: Any | None):
        self._client_response: ClientResponse = client_response
        self._response_body: str = response_body
        self._parsed_json: Any | None = parsed_json

    @property
    def status_code(self) -> int:
        return self._client_response.status

    @property
    def text(self) -> str:
        return self._response_body

    async def json(self) -> Any | None:
        return self._parsed_json


class AioHttpBackend(AbstractAsyncBackend, HTTPBackend):
    def __init__(
        self,
        auth_client: AuthClient,
        timeout_seconds: float = 10.0,
        request_hooks: list[RequestHook] | None = None,
    ):
        super().__init__(auth_client, request_hooks)
        self._client_timeout: ClientTimeout = ClientTimeout(total=timeout_seconds)
        self._client_session: ClientSession = ClientSession(timeout=self._client_timeout)

    async def request(self, http_method: str, endpoint_url: str, **request_params: Any) -> BaseResponse:
        async def execute_request(method_: str, url_: str, token: str, **params: Any) -> BaseResponse:
            headers: dict[str, str] = params.pop("headers", {})
            headers["Bearer"] = token

            async with self._client_session.request(
                method=http_method, url=endpoint_url, headers=headers, **params
            ) as client_response:
                response_body: str = await client_response.text()
                try:
                    parsed_json: Any | None = await client_response.json()
                except ContentTypeError:
                    parsed_json = None

                return AioHttpResponseAdapter(client_response, response_body, parsed_json)

        return await self._request_with_auth(
            http_method,
            endpoint_url,
            execute_request=execute_request,
            **request_params,
        )

    async def aclose(self) -> None:
        await self._client_session.close()
