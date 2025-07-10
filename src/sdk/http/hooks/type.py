from typing import Any, Awaitable, Callable


RequestHook = Callable[[str, str, dict[str, Any]], Awaitable[None]]


def request_hook(func: RequestHook) -> RequestHook:
    """
    Decorator to mark a function as a request middleware hook.

    Args:
        func (RequestHook): The function to be decorated.
    
    FunctionArgs:
        method (str): HTTP method (e.g., GET, POST)
        url (str): Full URL of the request
        kwargs (dict[str, Any]): Additional arguments passed to the HTTP request (e.g., headers, params, json)

    Example:
        @request_hook
        async def log_request(method, url, kwargs):
            ...
    """
    return func
