import os
import yaml
from sdk.utils.logger import logger
from dotenv import load_dotenv

from sdk.utils.exceptions import SDKConfigError


env_loaded = load_dotenv()

if not env_loaded:
    logger.warning("Environment variables not loaded. Ensure .env file exists or load manually.")


class SDKConfig:
    """
    SDKConfig loads and manages configuration settings for the Offers SDK.

    It supports a layered priority configuration system:
      1. Explicit constructor arguments
      2. Environment variables
      3. YAML configuration file (default: "config.yaml")
      4. Defaults (when none of the above are set)

    This class resolves essential runtime values like API base URL,
    refresh token, and the HTTP backend to use for sending requests.

    Attributes:
        api_base_url (str): The base URL of the Offers API.
        refresh_token (str): The long-lived refresh token used for authentication.
        backend (str): The name of the HTTP backend to use: 'httpx', 'aiohttp', or 'requests'.
    """
    def __init__(
        self,
        *,
        refresh_token: str | None = None,
        api_base_url: str | None = None,
        backend: str | None = None,
        config_path: str | None = None,
        ttl_seconds: int | None = None,
    ) -> None:
        """
        Initializes the SDK configuration.

        Args:
            refresh_token (str | None): Optional explicit refresh token.
                If not provided, it will be read from the REFRESH_TOKEN env var or config file.
            api_base_url (str | None): Optional explicit API base URL.
                If not provided, it will be read from the API_BASE_URL env var or config file.
            backend (str | None): Optional HTTP backend to use: 'httpx', 'aiohttp', or 'requests'.
                If not provided, it will be read from the BACKEND env var or config file.
            config_path (str): Path to a YAML config file with fallback values.
        """
        self._config: dict[str, str] = {}
        if config_path:
            self._load_config_file(config_path)

        self.api_base_url = self._get_value(
            direct_arg=api_base_url,
            env_key="API_BASE_URL",
            config_key="api_base_url",
            default=""
        )
        self.refresh_token = self._get_value(
            direct_arg=refresh_token,
            env_key="REFRESH_TOKEN",
            config_key="refresh_token",
            default=""
        )
        self.backend = self._get_value(
            direct_arg=backend,
            env_key="BACKEND",
            config_key="backend",
            default="httpx"
        )

        self.ttl_seconds = int(self._get_value(
            direct_arg=ttl_seconds,
            env_key="TTL_SECONDS",
            config_key="ttl_seconds",
            default=60
        ))

        if not self.api_base_url:
            raise SDKConfigError("API base URL must be set.")
        if not self.refresh_token:
            raise SDKConfigError("Refresh token must be set.")
        if self.backend not in ("httpx", "aiohttp", "requests"):
            raise SDKConfigError(f"Invalid backend: {self.backend}")

        logger.debug(f"Configuration: "
                     f"base_url={self.api_base_url}, refresh_token={self.refresh_token}, backend={self.backend}, "
                     f"ttl_seconds={self.ttl_seconds}, config_path={config_path}")

    def _load_config_file(self, config_path: str) -> None:
        """
        Loads configuration values from a YAML file, if it exists.

        Args:
            config_path (str): Path to the configuration file.

        Side Effects:
            Sets self._config to a dictionary of config values,
            or an empty dict if the file doesn't exist or fails to parse.
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                try:
                    self._config = yaml.safe_load(f) or {}
                except yaml.YAMLError as e:
                    logger.warning(f"YAML parsing error in {config_path}: {e}")
                    self._config = {}
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.warning(f"Could not open config file {config_path}: {e}")
            self._config = {}

    def _get_value(
        self,
        direct_arg: str | None,
        env_key: str,
        config_key: str,
        default: str
    ) -> str:
        """
        Resolves a configuration value using layered priority.

        Priority:
            1. Direct argument
            2. Environment variable
            3. YAML config file
            4. Default fallback

        Args:
            direct_arg (str | None): Value provided explicitly in the constructor.
            env_key (str): Environment variable key to check.
            config_key (str): Key in the config file to check.
            default (str): Fallback value if nothing else is set.

        Returns:
            str: The resolved configuration value.
        """
        if direct_arg is not None:
            return direct_arg
        
        env_value = os.getenv(env_key)
        if env_value and env_value.strip():
            return env_value.strip()
        
        return self._config.get(config_key, default)
