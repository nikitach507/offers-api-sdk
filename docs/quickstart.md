# Quickstart Guide

The **Offers API SDK** makes it easy to integrate with the Offers microservice.
It allows you to register products and retrieve offers through a simple, unified Python interface. The `OffersClient` class is the main entry point for working with the Offers SDK. It provides a unified interface to interact with both Products and Offers APIs.

## Key Capabilities

- Register products using the **Products API**

- Fetch offers based on product IDs via the **Offers API**

- Customize requests/responses with **plugin** support

- Inject **request hooks** for advanced use cases (e.g., logging, tracing)

- Configure the SDK flexibly through **arguments, environment variables, or YAML file**

## Installation

You can install the Offers API SDK using TestPyPI or directly from source.

### From TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ offers-api-sdk

```

### From Source

Clone this repository and install the package:

```bash
git clone https://github.com/nikitach507/offers-api-sdk

cd offers-api-sdk
```

## Usage Examples

`OffersClient` is asynchronous and should be properly closed after use. You can use it either with an async with block or manually call `.aclose()` when you're done.

### Using async with (recommended)

```python
from sdk import OffersClient

async def main():
    async with OffersClient(
        base_url="https://api.example.com",
        refresh_token="your-refresh-token"
    ) as client:
        product = await client.products.register_product({...})
        offers = await client.offers.get_offers(product_id)
```

### Manual Usage

```python
from sdk import OffersClient

async def main():
    client = OffersClient(
        base_url="https://api.example.com",
        refresh_token="your-refresh-token"
    )
    try:
        product = await client.products.register_product({...})
        offers = await client.offers.get_offers(product_id)
    finally:
        await client.aclose()
```

> [!TIP]  
> For quick testing and experimentation, try using the [Offers Client CLI](cli_usage.md) provided with the SDK.

## Authentication

All API requests are authenticated using a `refresh_token`. This token is required and must be provided either:

- Explicitly via constructor arguments: `config_file_path`

- Through the environment variable: `REFRESH_TOKEN`

- Inside a config YAML file: `config_file`

Without a valid `refresh_token`, the SDK will raise an error during initialization.

## Configuration Hierarchy

The SDK loads configuration using the following priority:

1. **Explicit Arguments**: Any parameters passed directly into the OffersClient() constructor take precedence over all other sources.

2. **Environment Variables**: If not provided via arguments, the SDK will check environment variables.

3. **Configuration File (config.yaml)**: If no arguments or environment variables are provided, the SDK will fall back to a config file.

4. **Defaults**: If nothing is provided, safe defaults will be used (e.g., backend is httpx, TTL is 60 seconds).

More details are available in [Configuration](configuration.md).

## Constructor Parameters

| Parameter            | Type                        | Description                                                                 |
|----------------------|-----------------------------|-----------------------------------------------------------------------------|
| base_url           | str               | **Required.** Base URL of the Offers API.                                  |
| refresh_token      | str               | **Required.** Used for authentication.                                     |
| backend_name       | str               | Optional. One of "httpx", "aiohttp", "requests". Defaults to "httpx". |
| config_file_path   | str               | Optional. Path to a .yaml config file.                                   |
| cache_ttl_seconds  | int               | Optional. TTL for offer caching. Defaults to 60.                           |
| plugins            | list[Plugin]     | Optional. List of plugins for request/response modification.               |
| request_hooks      | list[RequestHook] | Optional. Functions to intercept and modify outgoing HTTP requests.        |
| auth_client_factory| Callable[..., AuthClient]| Internal. Used to override the default auth client.                        |

## Available APIs

After initializing the client, you can access the following APIs:

- `client.products` — for product registration and management

- `client.offers` — for retrieving offers for products

See [API Reference](api_reference.md) for detailed usage.


## Plugins

You can pass plugins at initialization or register them later using register_plugins().

```python
client = OffersClient(..., plugins=[MyCustomPlugin])
client.register_plugins(MyCustomPlugin())
```

Plugins can:

- Modify outgoing requests (RequestPlugin)
- Handle or transform incoming responses (ResponsePlugin)

See [Plugins](plugins.md) for detailed usage.

## Request Hooks

Request hooks allow you to intercept and inspect outgoing HTTP requests before they are sent. This can be useful for:

- Debugging / Logging

- Tracing

- Injecting headers, etc.

### Usage Example

> [!IMPORTANT]  
> To define a request hook, decorate your async function with @request_hook. This tells the SDK to treat your function as a valid middleware.

```python
from sdk import OffersClient
from sdk.http.hooks import request_hook

@request_hook
async def log_request(method: str, url: str, kwargs: dict):
    print(f"[DEBUG] {method} {url}")

client = OffersClient(
    refresh_token="your-refresh-token",
    base_url="https://api.example.com",
    request_hooks=[log_request]
)
```

### Hook Signature

```python
Callable[[method: str, url: str, kwargs: dict[str, Any]], Awaitable[None]]
```

- `method`: HTTP method (e.g., "GET", "POST")

- `url`: Full request URL

- `kwargs`: Additional parameters passed to the request (e.g., headers, json, params)

Hooks must be asynchronous functions (async def). The SDK will await them before sending the actual request.

See [Middleware Hooks](hooks.md) for examples and usage.


## Summary

The OffersClient class is the central interface for working with the Offers SDK. It encapsulates configuration, authentication, plugin management, and API access. Use it to register products, fetch offers, and extend functionality via plugins and hooks.

For additional topics, see:

- **API Reference:** [api_reference.md](api_reference.md)

- **Configuration:** [configuration.md](configuration.md)

- **Plugins:** [plugins.md](plugins.md)

- **Hooks:** [hooks.md](hooks.md)

- **CLI Usage:** [cli_usage.md](cli_usage.md)