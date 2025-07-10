from abc import ABC, abstractmethod
from typing import Any

from sdk.http.interfaces import BaseResponse


class Plugin(ABC):
    """
    Abstract base class for all plugins.

    Plugins are used to extend the functionality of the SDK by processing
    HTTP requests and responses. Subclasses should implement specific
    behaviors for request or response handling.
    """
    pass


class RequestPlugin(Plugin):
    @abstractmethod
    async def process_request(self, method: str, url: str, kwargs: dict[str, Any]) -> None:
        """
        Process an HTTP request before it is sent.

        This method is called before each HTTP request is executed. It allows
        for modifications to the request, such as adding headers, logging,
        or injecting additional parameters.

        Args:
            method (str): The HTTP method (e.g., GET, POST).
            url (str): The full URL of the request, including the host.
            kwargs (dict[str, Any]): Additional arguments that will be passed
                to the HTTP request, such as headers, JSON payload, or query
                parameters.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """


class ResponsePlugin(Plugin):
    @abstractmethod
    async def process_response(self, response: BaseResponse) -> None:
        """
        Process an HTTP response after it is received.

        This method is called after each HTTP response is received. It allows
        for actions such as logging, validation, recording metrics, or
        propagating errors based on the response content.

        Args:
            response (BaseResponse): The HTTP response object, which includes
                attributes like status_code, text, and JSON content.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
