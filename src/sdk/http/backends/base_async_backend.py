from abc import ABC
from typing import Any, Awaitable, Callable

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from sdk.auth.client import AuthClient
from sdk.http.hooks.type import RequestHook
from sdk.http.interfaces import BaseResponse
from sdk.utils.logger import logger
from sdk.utils.exceptions import OffersAPIError, RequestExecutionError


class AbstractAsyncBackend(ABC):
    def __init__(self, auth_client: AuthClient, request_hooks: list[RequestHook] | None = None):
        self.auth_client: AuthClient = auth_client
        self._request_hooks: list[RequestHook] = request_hooks or []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        retry=retry_if_exception_type((OSError, RuntimeError)),
        reraise=True,
    )
    async def _request_with_auth(
        self,
        http_method: str,
        endpoint_url: str,
        *,
        execute_request: Callable[[str, str, str], Awaitable[BaseResponse]],
        **request_params: Any,
    ) -> BaseResponse:
        """
        Perform an authenticated HTTP request with retry logic.

        Args:
            http_method (str): HTTP method (e.g., 'GET', 'POST').
            endpoint_url (str): Target URL for the request.
            execute_request (Callable[[str, str, Any], BaseResponse]): Function to execute the HTTP request.
            **request_params (Any): Additional parameters for the request.

        Returns:
            BaseResponse: The HTTP response.

        Raises:
            OffersAPIError: If a request hook fails.
            RequestExecutionError: If the request execution fails.
        """
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
            response: BaseResponse = await execute_request(http_method, endpoint_url, access_token, **request_params)
        except RequestExecutionError as request_error:
            raise request_error

        if response.status_code == 401 and "Access token expired" in response.text:
            new_access_token: str | None = await self.auth_client.get_access_token(force_refresh=True)
            if not new_access_token:
                raise OffersAPIError("Failed to retrieve refreshed access token.")

            logger.debug("Retrying request with refreshed access token...")

            try:
                response: BaseResponse = await execute_request(
                    http_method,
                    endpoint_url,
                    new_access_token,
                    **request_params
                )
            except RequestExecutionError as retry_error:
                raise retry_error

        return response
