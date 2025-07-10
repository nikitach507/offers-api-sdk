import asyncio
from typing import Any

from pydantic import ValidationError

from sdk.api.base_api import BaseAPI
from sdk.api.constatns import PRODUCTS_ENDPOINT, HTTPMethod
from sdk.utils.logger import logger
from sdk.utils.exceptions import OffersAPIError, RequestExecutionError


class ProductsAPI(BaseAPI):
    async def register_products(self, product_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Register multiple products concurrently.

        Args:
            product_list (list[dict[str, Any]]): List of product data.

        Returns:
            list[dict[str, Any]]: List of registered products.
        """
        tasks: list[Any] = [
            self.register_product(product_data) for product_data in product_list
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        registered_products: list[dict[str, Any]] = []
        for index, result in enumerate(results):
            if isinstance(result, ValidationError):
                logger.warning(f"Validation failed on product #{index}: {result}")
            elif isinstance(result, (OffersAPIError, RequestExecutionError)):
                logger.error(f"API error on product #{index}: {result}")
            elif isinstance(result, Exception):
                logger.error(f"Unexpected error on product #{index}: {result}")
            else:
                registered_products.append(result)

        return registered_products

    async def register_product(self, product_data: dict[str, Any]) -> dict[str, Any]:
        """
        Register a new product.

        Args:
            product_data (dict[str, Any]): Dictionary with keys `id`, `name`, `description`.

        Returns:
            dict[str, Any]: The registered product data.

        Raises:
            OffersAPIError: If the response contains invalid JSON.
        """
        response = await self._request(
            http_method=HTTPMethod.POST,
            endpoint_path=PRODUCTS_ENDPOINT,
            json=product_data
        )
        logger.debug(f"Registering Response status code: {response.status_code}")

        try:
            response_data: dict[str, Any] = await response.json()
        except (ValueError, TypeError) as error:
            raise OffersAPIError(f"Invalid JSON in register_product response: {error}") from error

        logger.debug(f"Registering Response data: {response_data}")
        return response_data
