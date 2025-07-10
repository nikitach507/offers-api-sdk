from typing import Any

from sdk.api.constatns import HTTPMethod
from sdk.http.interfaces import BaseResponse, HTTPBackend
from sdk.utils.logger import logger
from sdk.plugins.interfaces import RequestPlugin, ResponsePlugin
from sdk.utils.exceptions import OffersAPIError, PluginError, RequestExecutionError
from sdk.http.utils import raise_for_status_with_text


class BaseAPI:
    def __init__(
        self,
        http_backend: HTTPBackend,
        base_url: str
    ) -> None:
        self._http_backend: HTTPBackend = http_backend
        self._base_url: str = base_url
        self._request_plugins: list[RequestPlugin] = []
        self._response_plugins: list[ResponsePlugin] = []

    def set_plugins(self, request_plugins: list[RequestPlugin], response_plugins: list[ResponsePlugin]) -> None:
        """
        Set the request and response plugins for the API.

        Args:
            request_plugins (list[RequestPlugin]): Plugins to process requests.
            response_plugins (list[ResponsePlugin]): Plugins to process responses.
        """
        self._request_plugins = request_plugins
        self._response_plugins = response_plugins

    async def _request(
        self,
        http_method: HTTPMethod,
        endpoint_path: str,
        **request_params: Any,
    ) -> BaseResponse:
        """
        Perform an HTTP request with plugins and error handling.

        Args:
            http_method (HTTPMethod): The HTTP method to use (e.g., GET, POST).
            endpoint_path (str): The endpoint path to append to the base URL.
            **request_params (Any): Additional parameters for the HTTP request.

        Returns:
            BaseResponse: The HTTP response.

        Raises:
            PluginError: If a plugin fails during request or response processing.
            OffersAPIError: If the API response indicates an error.
        """
        full_url: str = f"{self._base_url}{endpoint_path}"
        logger.debug(f"[{self.__class__.__name__}] {http_method} {full_url} | {request_params=}")

        # Process request plugins
        for request_plugin in self._request_plugins:
            try:
                await request_plugin.process_request(http_method, full_url, request_params)
            except Exception as plugin_error:
                raise PluginError(f"Request plugin {request_plugin.__class__.__name__} failed: {str(plugin_error)}")

        try:
            response: BaseResponse = await self._http_backend.request(http_method, full_url, **request_params)
        except RequestExecutionError as execution_error:
            raise execution_error

        # Process response plugins
        for response_plugin in self._response_plugins:
            try:
                await response_plugin.process_response(response)
            except Exception as plugin_error:
                raise PluginError(f"Response plugin {response_plugin.__class__.__name__} failed: {str(plugin_error)}")

        try:
            raise_for_status_with_text(response)
        except OffersAPIError as api_error:
            logger.warning(f"API error on {http_method} {full_url}: {api_error}")
            raise

        return response
