# Plugins

The Offers SDK allows you to extend the functionality of the SDK using plugins. Plugins give you the ability to modify API-level behavior and customize how requests and responses are handled at the Products API and Offers API level.

There are two main types of plugins:

- **Request Plugins**: These plugins modify the HTTP requests before they are sent to the server. You can add custom headers, modify parameters, or log requests.

- **Response Plugins**: These plugins modify or handle the HTTP responses after they are received. You can use them for logging, error handling, or data transformation.

## Example of Using Plugins

You can register plugins when you initialize the `OffersClient`, or you can add them later using the `register_plugins()` method.

### Registering Plugins at Initialization

```python
client = OffersClient(
    base_url="https://api.example.com",
    refresh_token="your-refresh-token",
    plugins=[MyCustomRequestPlugin(), MyCustomResponsePlugin()]
)
```

### Registering Plugins After Initialization

```python
client = OffersClient(
    base_url="https://api.example.com",
    refresh_token="your-refresh-token"
)

client.register_plugins(MyCustomRequestPlugin())
client.register_plugins(MyCustomResponsePlugin())
```

## Creating Your Own Plugins

To create a custom plugin, you need to subclass either RequestPlugin or ResponsePlugin. Both subclasses require you to implement specific methods:

### 1. Creating a Request Plugin

A `RequestPlugin` lets you modify the HTTP request before it is sent. For instance, you might want to add custom headers or log the request details.

```python
from sdk.http.hooks import RequestPlugin

class MyCustomRequestPlugin(RequestPlugin):
    async def process_request(self, method: str, url: str, kwargs: dict[str, Any]) -> None:
        print(f"Sending {method} request to {url}")
        print(f"Request parameters: {kwargs}")
```


### 2. Creating a Response Plugin

A `ResponsePlugin` lets you handle the HTTP response after it is received. This is useful for logging, handling errors, or performing additional validation.

```python
from sdk.http.hooks import ResponsePlugin
from sdk.http.interfaces import BaseResponse

class MyCustomResponsePlugin(ResponsePlugin):
    async def process_response(self, response: BaseResponse) -> None:
        print(f"Received response: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
```

## Registering Plugins

Once you've created your custom plugins, you can register them with the `OffersClient` instance using `register_plugins()`.

```python
client.register_plugins(MyCustomRequestPlugin())
client.register_plugins(MyCustomResponsePlugin())
```

You can also pass them at initialization as shown in the examples above.

## Summary

Plugins in the Offers SDK allow you to easily extend its functionality. Whether you need to modify requests, handle responses, or log information, plugins are a powerful way to customize your SDK usage.

### Key Points

- **Request Plugins**: Modify requests before they are sent to the server.

- **Response Plugins**: Modify or inspect responses after they are received.

- **Custom Plugins**: Create your own plugins by subclassing `RequestPlugin` or `ResponsePlugin`.

- **Register Plugins**: Register plugins via initialization or `register_plugin()`.
