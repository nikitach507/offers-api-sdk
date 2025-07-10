import asyncio
from typing import Any

import requests
from requests import RequestException
from requests import Response as RequestsResponse
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from sdk.auth.client import AuthClient
from sdk.http.hooks.type import RequestHook
from sdk.http.interfaces import BaseResponse, HTTPBackend
from sdk.utils.logger import logger
from sdk.utils.exceptions import OffersAPIError, RequestExecutionError


class RequestsResponseAdapter(BaseResponse):
    def __init__(self, requests_response: RequestsResponse):
        self._requests_response: RequestsResponse = requests_response

    @property
    def status_code(self) -> int:
        return self._requests_response.status_code

    @property
    def text(self) -> str:
        return self._requests_response.text

    async def json(self) -> dict[str, Any] | list[Any] | None:
        return await asyncio.to_thread(self._requests_response.json)


class RequestsBackend(HTTPBackend):
    def __init__(
        self,
        auth_client: AuthClient,
        timeout_seconds: float = 10.0,
        request_hooks: list[RequestHook] | None = None,
    ):
        self.auth_client: AuthClient = auth_client
        self._timeout_seconds: float = timeout_seconds
        self._session: requests.Session = requests.Session()
        self._request_hooks: list[RequestHook] = request_hooks or []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        retry=retry_if_exception_type(RequestException),
        reraise=True,
    )
    async def request(self, http_method: str, endpoint_url: str, **request_params: Any) -> BaseResponse:
        def execute_request_with_token(access_token: str) -> RequestsResponse:
            headers: dict[str, str] = request_params.get("headers", {})
            headers["Bearer"] = access_token
            return self._session.request(
                method=http_method, url=endpoint_url, timeout=self._timeout_seconds, headers=headers, **request_params
            )

        access_token: str | None = await self.auth_client.get_access_token()
        if not access_token:
            raise OffersAPIError("Failed to retrieve access token.")

        # Execute request hooks before making the request
        for hook in self._request_hooks:
            try:
                await hook(http_method, endpoint_url, request_params)
            except Exception as hook_error:
                raise OffersAPIError(f"Request hook {hook.__class__.__name__} failed: {hook_error}") from hook_error

        try:
            response: RequestsResponse = await asyncio.to_thread(execute_request_with_token, access_token)

            if response.status_code == 401 and "Access token expired" in response.text:
                new_access_token: str | None = await self.auth_client.get_access_token(force_refresh=True)
                if not new_access_token:
                    raise OffersAPIError("Failed to retrieve refreshed access token.")

                logger.debug("Retrying request with refreshed access token...")
                response = await asyncio.to_thread(execute_request_with_token, new_access_token)

            return RequestsResponseAdapter(response)

        except RequestException as request_exception:
            raise RequestExecutionError(f"Network error (requests): {request_exception}") from request_exception

    async def close(self) -> None:
        self._session.close()
