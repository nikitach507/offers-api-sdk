import asyncio
from typing import Any

from sdk.api.products import ProductsAPI


class SyncProductsAPI:
    def __init__(self, products_api: ProductsAPI, event_loop: asyncio.AbstractEventLoop) -> None:
        """
        Initialize the synchronous products API wrapper.

        Args:
            products_api (ProductsAPI): The asynchronous ProductsAPI instance.
            event_loop (asyncio.AbstractEventLoop): The event loop to run asynchronous tasks.
        """
        self._products_api: ProductsAPI = products_api
        self._event_loop: asyncio.AbstractEventLoop = event_loop

    def register_product(self, product_data: dict[str, Any]) -> dict[str, Any]:
        """
        Register a new product synchronously.

        Args:
            product_data (dict[str, Any]): The product data to register.

        Returns:
            dict[str, Any]: The registered product data.
        """
        return self._event_loop.run_until_complete(self._products_api.register_product(product_data))

    def register_products(self, product_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Register multiple products synchronously.

        Args:
            product_list (list[dict[str, Any]]): A list of product data to register.

        Returns:
            list[dict[str, Any]]: A list of registered product data.
        """
        return self._event_loop.run_until_complete(self._products_api.register_products(product_list))
