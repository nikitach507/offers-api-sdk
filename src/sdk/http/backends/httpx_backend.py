from typing import Any

import httpx

from sdk.auth.client import AuthClient
from sdk.http.backends.base_async_backend import AbstractAsyncBackend
from sdk.http.hooks.type import RequestHook
from sdk.http.interfaces import BaseResponse, HTTPBackend
from sdk.utils.exceptions import RequestExecutionError


class HttpxResponseAdapter(BaseResponse):
    def __init__(self, httpx_response: httpx.Response):
        self._httpx_response: httpx.Response = httpx_response

    @property
    def status_code(self) -> int:
        return self._httpx_response.status_code

    @property
    def text(self) -> str:
        return self._httpx_response.text

    async def json(self) -> Any:
        return self._httpx_response.json()


class HttpxBackend(AbstractAsyncBackend, HTTPBackend):
    def __init__(
        self,
        auth_client: AuthClient,
        timeout_seconds: float = 10.0,
        request_hooks: list[RequestHook] | None = None,
    ):
        super().__init__(auth_client, request_hooks)
        self._httpx_client: httpx.AsyncClient = httpx.AsyncClient(
            timeout=timeout_seconds,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=10),
        )

    async def request(self, http_method: str, endpoint_url: str, **request_params: Any) -> BaseResponse:
        async def execute_request(method_: str, url_: str, token: str, **params: Any) -> BaseResponse:
            headers: dict[str, str] = params.pop("headers", {})
            headers["Bearer"] = token
            try:
                httpx_response: BaseResponse = await self._httpx_client.request(
                    method=http_method, url=endpoint_url, headers=headers, **params
                )
            except httpx.RequestError as httpx_error:
                raise RequestExecutionError(f"HTTPX request failed: {str(httpx_error)}") from httpx_error

            return HttpxResponseAdapter(httpx_response)

        return await self._request_with_auth(
            http_method,
            endpoint_url,
            execute_request=execute_request,
            **request_params,
        )

    async def aclose(self) -> None:
        await self._httpx_client.aclose()
