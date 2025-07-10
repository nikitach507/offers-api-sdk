# API Reference

The Offers SDK provides simple, high-level interfaces to interact with your product catalog and associated offers. These APIs are exposed via two components: `products` and `offers`, accessible from the `OffersClient` instance.

## Products API

Use the Products API to register one or multiple products with the Offers microservice.

### Register a Single Product

```python
product = await client.products.register_product({
    "id": "product-uuid-123",
    "name": "Samsung Galaxy S22",
    "description": "128GB, Phantom Black"
})
```

### Register Multiple Products

```python
products = await client.products.register_products([
    {"id": "product-uuid-123", "name": "Samsung Galaxy S22", "description": "128GB, Black"},
    {"id": "product-uuid-123", "name": "iPhone 13", "description": "256GB, Blue"},
])
```

> [!NOTE]  
> Each product must include at minimum: `id`, `name`, and `description`.

- The SDK automatically performs concurrent registration of all products and handles validation errors gracefully.

- Any failed entries will be logged without interrupting the process.

## Offers API

The Offers API allows you to fetch available offers for a specific product by its UUID. Responses are automatically validated and cached to avoid redundant API calls.

### Retrieve Offers for a Product

```python
offers = await client.offers.get_offers(product_id)
```

> [!NOTE]  
> Offers are automatically re-fetched once the cache expires.

- Returns a list of validated `Offer` objects.

- Caches results in memory for the duration of `cache_ttl_seconds` (default: 60 seconds).

- Automatically skips API calls if fresh cached data exists.

## HTTP Backends

The SDK supports multiple HTTP clients under the hood, giving you full control over which library to use for outgoing requests.

### Supported Backends

- `httpx` (default, async)

- `aiohttp` (async)

- `requests` (sync, internally adapted to async)

### Switching Backends

You can switch backends using the `backend_name` parameter:

```python
client = OffersClient(
    base_url="https://api.example.com",
    refresh_token="your-token",
    backend_name="aiohttp"
)
```

### Why Use a Custom Backend?

Different environments and requirements may benefit from different HTTP clients. For example:

- Use `httpx` for most modern async Python projects.

- Use `aiohttp` if you already use it elsewhere in your stack.

- Use `requests` if integrating with legacy systems or synchronous tools.

> [!TIP]  
> If you’re unsure, stick with the default `httpx` — it provides excellent performance and full compatibility.

## Summary

The Offers SDK gives you simple but powerful tools to:

- Register products via `client.products`

- Fetch offers via `client.offers`

- Choose between multiple HTTP clients via `backend_name`

You can seamlessly plug these APIs into your data pipelines, microservices, or backend logic, while maintaining full control over authentication, configuration, and behavior.