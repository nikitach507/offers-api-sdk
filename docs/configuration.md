# Configuration

The SDK allows users to configure its parameters using a combination of **explicit arguments**, **environment variables**, and a **configuration file**. This layered approach ensures flexibility while maintaining clear precedence rules for how configuration values are applied.

## Configuration Hierarchy

The configuration system follows this priority order:

1. **Explicit Arguments**: Any configuration passed directly during the initialization of `OffersClient` will have the highest priority.

2. **Environment Variables**: If a configuration option is not provided via arguments, the SDK will attempt to read it from environment variables.

3. **Configuration File (`config.yaml`)**: If neither arguments nor environment variables provide the configuration, the SDK will fall back to reading from the `config.yaml` file.

> [!NOTE]  
> To use a config file, you must either pass its path as an explicit argument (config_file_path="..."), or set the environment variable CONFIG_PATH="...".

4. **Defaults**: If all the above sources are absent, default values will be applied (e.g., default backend `httpx` and TTL of 60 seconds).

## Configuration Options

The SDK supports the following configuration options, which can be set via the constructor, environment variables, or `config.yaml`. Below, you’ll find each option’s details, examples, and how the values are sourced.

### Required Parameters

These parameters must be provided in at least one of the following sources: constructor arguments, environment variables, or `config.yaml` file. If missing, an error will occur.

#### `api_base_url`

- **Description**: The base URL for the Offers API.
- **Requirement**: Required for the SDK to function. If not provided, an error will be raised.
- **Examples**:
  - As an argument: `OffersClient(base_url="https://api.example.com")`
  - As an environment variable: `API_BASE_URL=https://api.example.com`
  - In `config.yaml`:
    ```yaml
    api_base_url: "https://api.example.com"
    ```

#### `refresh_token`

- **Description**: The refresh token used for authentication.
- **Requirement**: Required for the SDK to authenticate API requests. If missing, an error will be raised.
- **Examples**:
  - As an argument: `OffersClient(refresh_token="your-refresh-token")`
  - As an environment variable: `REFRESH_TOKEN=your-refresh-token`
  - In `config.yaml`:
    ```yaml
    refresh_token: "your-refresh-token"
    ```

### Optional Parameters

These parameters are optional and will default to predefined values if not provided.

#### `backend`

- **Description**: The HTTP backend to use. Choose between:
  - `httpx`
  - `aiohttp`
  - `requests`
- **Default**: Defaults to `httpx` if not provided.
- **Examples**:
  - As an argument: `OffersClient(backend_name="aiohttp")`
  - As an environment variable: `BACKEND=aiohttp`
  - In `config.yaml`:
    ```yaml
    backend: "aiohttp"
    ```

#### `ttl_seconds`

- **Description**: The time-to-live (TTL) for cached offer data in seconds.
- **Default**: Defaults to 60 seconds if not provided.
- **Examples**:
  - As an argument: `OffersClient(cache_ttl_seconds=120)`
  - As an environment variable: `TTL_SECONDS=120`
  - In `config.yaml`:
    ```yaml
    ttl_seconds: 120
    ```

## Example Configuration Files

### Example `.env` File

```env
API_BASE_URL=https://api.example.com
REFRESH_TOKEN=your-refresh-token
BACKEND=httpx
TTL_SECONDS=20
```

### Example `config.yaml` File

```yaml
api_base_url: "https://api.example.com"
refresh_token: "your-refresh-token"
backend: "requests"
ttl_seconds: 90
```