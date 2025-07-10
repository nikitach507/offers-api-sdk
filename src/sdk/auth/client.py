import time

import httpx
from pydantic import ValidationError

from sdk.auth.constants import AUTH_ENDPOINT, TOKEN_LIFETIME_SECONDS
from sdk.utils.logger import logger
from sdk.models.auth import AuthApiResponse
from sdk.utils.exceptions import AuthRequestError


class AuthClient:
    def __init__(self, refresh_token: str | None, base_url: str | None = None) -> None:
        self._refresh_token: str | None = refresh_token
        self._base_url: str | None = base_url

        self._access_token: str | None = None
        self._token_expiry_timestamp: float = 0.0

    async def get_access_token(
            self,
            token_lifetime_seconds: int = TOKEN_LIFETIME_SECONDS,
            force_refresh: bool = False
    ) -> str | None:
        """
        Retrieve an access token, either from cache or by requesting a new one.

        Args:
            token_lifetime_seconds (int): The lifetime of the token in seconds. Defaults to 360 seconds.
            force_refresh (bool): If True, forces a new token request even if a cached token
                is valid. Defaults to False.

        Returns:
            str | None: The access token if available, otherwise None.

        Raises:
            AuthRequestError: If the refresh token is not set or if the token request fails.
        """
        if not self._refresh_token:
            raise AuthRequestError("Refresh token is not set. Please provide a valid refresh token.")

        if not force_refresh and self._access_token and time.time() < self._token_expiry_timestamp:
            logger.debug("Using cached access token.")
            return self._access_token

        logger.debug("Requesting new access token using refresh token.")

        self._access_token = await self._request_new_token(self._refresh_token)
        self._token_expiry_timestamp = time.time() + token_lifetime_seconds
        return self._access_token

    async def _request_new_token(self, refresh_token: str) -> str:
        """
        Request a new access token using the provided refresh token.

        Args:
            refresh_token (str): The refresh token to use for requesting a new access token.

        Returns:
            str: The newly obtained access token.

        Raises:
            AuthRequestError: If the base URL is not set, the request fails, or the response structure is invalid.
        """
        if not self._base_url:
            raise AuthRequestError("Base URL is not set. Please provide a valid base URL.")

        async with httpx.AsyncClient() as http_client:
            auth_url: str = f"{self._base_url}{AUTH_ENDPOINT}"
            headers: dict[str, str] = {"Bearer": refresh_token}
            logger.debug(f"Auth Request to: {auth_url}")

            try:
                response = await http_client.post(auth_url, headers=headers)
                response.raise_for_status()

            except httpx.HTTPStatusError as http_error:
                raise AuthRequestError(
                    f"Authentication failed with status code {http_error.response.status_code}: "
                    f"{http_error.response.text}"
                ) from http_error
            except httpx.RequestError as network_error:
                raise AuthRequestError(
                    f"Network error during authentication request: {str(network_error)}"
                ) from network_error

            try:
                auth_response = AuthApiResponse(**response.json())
                access_token: str = auth_response.access_token
                logger.debug(f"Received new access token: {access_token}")

            except (ValidationError, TypeError, ValueError) as parse_error:
                raise AuthRequestError(
                    f"Invalid response structure from auth service: {str(parse_error)}"
                ) from parse_error

            return access_token
