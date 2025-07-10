from typing import Any, Callable, TypeVar

from sdk.api.offers import OffersAPI
from sdk.api.products import ProductsAPI
from sdk.auth.client import AuthClient
from sdk.config.sdk_config import SDKConfig
from sdk.http.backends.aiohttp_backend import AioHttpBackend
from sdk.http.backends.httpx_backend import HttpxBackend
from sdk.http.backends.requests_backend import RequestsBackend
from sdk.http.hooks.type import RequestHook
from sdk.http.interfaces import HTTPBackend
from sdk.plugins.interfaces import Plugin, RequestPlugin, ResponsePlugin
from sdk.utils.exceptions import SDKConfigError

T = TypeVar("T", bound="OffersClient")


BACKEND_MAPPING: dict = {
    "httpx": HttpxBackend,
    "aiohttp": AioHttpBackend,
    "requests": RequestsBackend,
}


class OffersClient:
    """
    OffersClient is the main entry point for interacting with the Offers SDK.

    This client provides access to the Products and Offers APIs, allowing users
    to register products, fetch offers, and manage plugins for request and
    response processing.

    Examples:
        >>> from sdk import OffersClient
        >>> async with OffersClient(base_url="https://api.example.com") as client:
        >>>     await client.products.register_product({...})
        >>>     offers = await client.offers.get_offers(product_id)
    """

    def __init__(
        self,
        *,
        refresh_token: str | None = None,
        base_url: str | None = None,
        backend_name: str | None = None,
        config_file_path: str | None = None,
        cache_ttl_seconds: int | None = None,
        plugins: list[Plugin] | None = None,
        request_hooks: list[RequestHook] | None = None,
        auth_client_factory: Callable[..., AuthClient] = AuthClient
    ) -> None:
        """
        Initialize the OffersClient.

        Args:
            refresh_token (str | None): Token for authentication.
            base_url (str | None): Base URL for the API.
            backend_name (str | None): Name of the HTTP backend to use.
            config_file_path (str | None): Path to the configuration file.
            cache_ttl_seconds (int | None): Time-to-live for cached data.
            plugins (list[Plugin] | None): List of plugins for request/response processing.
            request_hooks (list[RequestHook] | None): Hooks for modifying requests.
            auth_client_factory (Callable[..., AuthClient]): Factory for creating the AuthClient.
        """
        # Initialize configuration
        try:
            self._config: SDKConfig = SDKConfig(
                refresh_token=refresh_token,
                api_base_url=base_url,
                backend=backend_name,
                config_path=config_file_path,
                ttl_seconds=cache_ttl_seconds
            )
        except SDKConfigError as config_error:
            raise ValueError("Failed to initialize SDK configuration.") from config_error

        # Initialize authentication client
        self._auth_client: AuthClient = auth_client_factory(
            refresh_token=self._config.refresh_token,
            base_url=self._config.api_base_url
        )

        # Initialize Middleware Hooks
        self._request_hooks: list[RequestHook] = request_hooks or []

        # Select the appropriate HTTP backend
        if self._config.backend not in BACKEND_MAPPING:
            raise ValueError(
                f"Unsupported backend: {self._config.backend}. "
                f"Supported backends: {', '.join(BACKEND_MAPPING.keys())}"
            )

        backend_cls = BACKEND_MAPPING[self._config.backend]

        self._http_backend: HTTPBackend = backend_cls(auth_client=self._auth_client, request_hooks=self._request_hooks)

        # Initialize API clients
        self.products: ProductsAPI = ProductsAPI(self._http_backend, self._config.api_base_url)
        self.offers: OffersAPI = OffersAPI(
            self._http_backend,
            self._config.api_base_url,
            cache_ttl_seconds=self._config.ttl_seconds
        )

        # Initialize API Plugins
        self._request_plugins: list[RequestPlugin] = []
        self._response_plugins: list[ResponsePlugin] = []

        for plugin in plugins or []:
            self.register_plugins(plugin)

    async def __aenter__(self: T) -> T:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http_backend.aclose()

    def __repr__(self) -> str:
        return f"OffersClient(base_url={self._config.api_base_url}, backend={self._config.backend})"

    def register_plugins(self, plugin: Plugin | list[Plugin]) -> None:
        """
        Register one or more plugins for request and response processing.

        Args:
            plugin (Plugin | list[Plugin]): A single plugin or a list of plugins to register.
        """
        if isinstance(plugin, Plugin):
            plugin = [plugin]

        for single_plugin in plugin:
            if isinstance(single_plugin, RequestPlugin) and single_plugin not in self._request_plugins:
                self._request_plugins.append(single_plugin)
            if isinstance(single_plugin, ResponsePlugin) and single_plugin not in self._response_plugins:
                self._response_plugins.append(single_plugin)

        self.products.set_plugins(self._request_plugins, self._response_plugins)
        self.offers.set_plugins(self._request_plugins, self._response_plugins)
