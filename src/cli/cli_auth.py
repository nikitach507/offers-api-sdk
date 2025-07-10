import json
import time
from asyncio.log import logger
from pathlib import Path
from typing import Any

from cli.constants import CACHE_PATH
from sdk.auth.client import AuthClient
from sdk.utils.exceptions import AuthRequestError


class CachedAuthClient(AuthClient):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._cache_path: Path = CACHE_PATH
        self._access_token: str | None = None
        self._token_expiry_timestamp: float | None = None
        try:
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            logger.warning(f"Cannot create cache directory {self._cache_path.parent}: {e}")
        self._load_cache()

    def _load_cache(self) -> None:
        if not self._cache_path.exists():
            return

        try:
            raw: str = self._cache_path.read_text(encoding="utf-8")
        except (OSError, PermissionError) as e:
            logger.warning(f"Failed to read cache file {self._cache_path}: {e}")
            return

        try:
            data: dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in cache file {self._cache_path}: {e}")
            return

        if (
                "access_token" in data and "token_expiry" in data and time.time() < data["token_expiry"]
        ):
            self._access_token = data["access_token"]
            self._token_expiry_timestamp = data["token_expiry"]

    def _save_cache(self) -> None:
        data: dict[str, Any] = {
            "access_token": self._access_token,
            "token_expiry": self._token_expiry_timestamp,
        }
        try:
            self._cache_path.write_text(json.dumps(data), encoding="utf-8")
        except (OSError, PermissionError, TypeError) as e:
            logger.warning(f"Failed to write cache file {self._cache_path}: {e}")

    async def get_access_token(self, expires_in_seconds: int = 360, force: bool = False) -> str | None:
        if not self._access_token or force:
            token: str | None = await super().get_access_token(expires_in_seconds, force)
            if token:
                self._access_token = token
                self._save_cache()
            else:
                raise AuthRequestError("Unable to obtain access token.")
        return self._access_token
