import asyncio
from typing import Any

from sdk.client import OffersClient
from sdk.sync.offers import SyncOffersAPI
from sdk.sync.products import SyncProductsAPI


class SyncOffersClient:
    def __init__(self, **client_kwargs: Any) -> None:
        """
        Initialize the synchronous offers client.

        Args:
            **client_kwargs (Any): Keyword arguments to configure the OffersClient.
        """
        self._event_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)

        self._client: OffersClient = OffersClient(**client_kwargs)

        self.products: SyncProductsAPI = SyncProductsAPI(self._client.products, self._event_loop)
        self.offers: SyncOffersAPI = SyncOffersAPI(self._client.offers, self._event_loop)

    def close(self) -> None:
        self._event_loop.run_until_complete(self._client.aclose())
        self._event_loop.close()

    def __enter__(self) -> "SyncOffersClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
