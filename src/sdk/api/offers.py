import time
from uuid import UUID

from pydantic import ValidationError

from sdk.api.base_api import BaseAPI
from sdk.api.constatns import GET_OFFERS_ENDPOINT, HTTPMethod
from sdk.http.interfaces import HTTPBackend
from sdk.utils.logger import logger
from sdk.models.offer import Offer
from sdk.utils.exceptions import OffersAPIError


class OffersAPI(BaseAPI):
    def __init__(
        self,
        http_backend: HTTPBackend,
        base_url: str,
        cache_ttl_seconds: int = 60,
    ) -> None:
        super().__init__(
            http_backend=http_backend,
            base_url=base_url,
        )
        self._cache_ttl_seconds: int = cache_ttl_seconds
        self._cache: dict[UUID, tuple[list[Offer], float]] = {}

    async def get_offers(self, product_id: UUID) -> list[Offer]:
        """
        Retrieve offers for a specific product.

        Args:
            product_id (UUID): The unique identifier of the product.

        Returns:
            list[Offer]: A list of offer models.

        Raises:
            OffersAPIError: If the response contains invalid offer data.
        """
        current_time: float = time.time()
        cached_data: tuple[list[Offer], float] | None = self._cache.get(product_id)

        if cached_data:
            offers, timestamp = cached_data
            if current_time - timestamp < self._cache_ttl_seconds:
                logger.debug(f"Returning cached offers for product_id: {product_id}")
                return offers
            else:
                logger.debug(f"Cache expired for product_id: {product_id}")
                self._cache.pop(product_id)

        logger.debug(f"Fetching offers for product_id: {product_id}")

        response = await self._request(
            http_method=HTTPMethod.GET,
            endpoint_path=GET_OFFERS_ENDPOINT.format(product_id=product_id),
        )

        logger.debug(f"Offers Response status code: {response.status_code}")
        try:
            response_data: list[dict] = await response.json()
            offers: list[Offer] = [Offer.model_validate(offer) for offer in response_data]
        except (ValidationError, ValueError, TypeError) as error:
            raise OffersAPIError(f"Invalid offer data in response: {str(error)}") from error

        logger.debug(f"Parsed {len(offers)} offers.")
        self._cache[product_id] = (offers, current_time)
        return offers
