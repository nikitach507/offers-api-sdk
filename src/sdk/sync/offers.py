import asyncio
from uuid import UUID

from sdk.api.offers import OffersAPI
from sdk.models.offer import Offer


class SyncOffersAPI:
    def __init__(self, offers_api: OffersAPI, event_loop: asyncio.AbstractEventLoop) -> None:
        """
        Initialize the synchronous offers API wrapper.

        Args:
            offers_api (OffersAPI): The asynchronous OffersAPI instance.
            event_loop (asyncio.AbstractEventLoop): The event loop to run asynchronous tasks.
        """
        self._offers_api: OffersAPI = offers_api
        self._event_loop: asyncio.AbstractEventLoop = event_loop

    def get_offers(self, product_id: UUID) -> list[Offer]:
        """
        Retrieve offers for a specific product synchronously.

        Args:
            product_id (UUID): The unique identifier of the product.

        Returns:
            list[Offer]: A list of offers for the specified product.
        """
        return self._event_loop.run_until_complete(self._offers_api.get_offers(product_id))
