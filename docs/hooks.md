# Middleware Request Hooks

Request hooks in the Offers SDK allow you to intercept and inspect outgoing HTTP requests before they are sent. This can be useful for a variety of purposes, such as:

- **Debugging / Logging**: Track what requests are being sent and their parameters.

- **Tracing**: Capture additional metadata for monitoring or performance analysis.

- **Injecting Headers**: Modify headers or add new ones before the request is sent.

## Usage Example

To use a request hook, you need to define an asynchronous function and decorate it with the `@request_hook` decorator. This decorator tells the SDK to treat your function as a valid middleware function for requests.

> [!IMPORTANT]
>Make sure to decorate your function with `@request_hook` so that the SDK recognizes it as a valid hook.

```python
from sdk import OffersClient
from sdk.http.hooks import request_hook

@request_hook
async def add_custom_header(method: str, url: str, kwargs: dict):
    kwargs["headers"]["X-Custom-Header"] = "MyCustomHeaderValue"

# Initialize the OffersClient with the custom request hook
client = OffersClient(
    refresh_token="your-refresh-token",
    base_url="https://api.example.com",
    request_hooks=[add_custom_header]
)
```

In this example:

- The request hook adds a custom header (`X-Custom-Header: MyCustomHeaderValue`) to the request before it is sent.

## Hook Signature

The signature for the request hook is as follows:

```python
Callable[[method: str, url: str, kwargs: dict[str, Any]], Awaitable[None]]
```

- `method`: HTTP method (e.g., `"GET"`, `"POST"`).

- `url`: Full request URL.

- `kwargs`: Additional parameters passed to the request (e.g., headers, JSON payload, query parameters).

## Registering Request Hooks

You can register your request hooks **only** at the time of `OffersClient` initialization.

```python
client = OffersClient(
    base_url="https://api.example.com",
    refresh_token="your-refresh-token",
    request_hooks=[log_request]
)
```

## Summary

Request hooks provide a flexible and powerful way to intercept and modify outgoing HTTP requests. They allow you to:

- Modify request parameters such as headers or query parameters.

- Add debugging or logging functionality.

- Implement custom behaviors before requests are sent.

By defining your own request hooks and applying them via the `@request_hook` decorator, you can easily integrate these hooks into the Offers SDK to suit your use case.
