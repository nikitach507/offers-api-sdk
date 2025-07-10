from sdk.http.interfaces import BaseResponse
from sdk.utils.logger import logger
from sdk.utils.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    OffersAPIError,
    RateLimitError,
    ServerError,
    TimeoutError,
)


def raise_for_status_with_text(response: BaseResponse) -> None:
    """
    Raise appropriate exceptions based on the HTTP response status code.

    Args:
        response (BaseResponse): The HTTP response object containing the
            status code and response text.

    Raises:
        AuthenticationError: If the status code is 401 (Unauthorized).
        NotFoundError: If the status code is 404 (Not Found).
        ConflictError: If the status code is 409 (Conflict).
        RateLimitError: If the status code is 429 (Too Many Requests).
        TimeoutError: If the status code is 408 (Request Timeout).
        ServerError: If the status code is 500 or higher (Server Error).
        OffersAPIError: For all other non-success status codes.
    """
    status_code: int = response.status_code
    response_text: str = response.text
    logger.debug(f"Response status: {status_code} | {response_text}")

    if 200 <= status_code < 400:
        return

    if status_code == 401:
        raise AuthenticationError(response_text)
    elif status_code == 404:
        raise NotFoundError(response_text)
    elif status_code == 408:
        raise TimeoutError(response_text)
    elif status_code == 409:
        raise ConflictError(response_text)
    elif status_code == 429:
        raise RateLimitError(response_text)
    elif status_code >= 500:
        raise ServerError(response_text)
    else:
        raise OffersAPIError(response_text, status_code=status_code)
