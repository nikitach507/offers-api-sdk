# CLI Usage Guide

The Offers SDK comes with a Command Line Interface (CLI) that allows you to quickly test and interact with the Offers API without needing to write complex code. The CLI can be used for tasks like registering products or retrieving offers associated with a specific product.

## Why Use the CLI?

The CLI is particularly useful for quick testing, debugging, and experimentation. It enables you to interact with the Offers SDK and perform operations such as:

- **Registering products** with the `register-product` command.

- **Retrieving offers** associated with a product using the `get-offers` command.

In addition, the CLI automatically handles authentication using the `CachedAuthClient`, which caches the `access_token` to a file, ensuring the token persists between tests and sessions.

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

## Usage .env File

To use the CLI, you'll need to set up your environment with the necessary configuration values. You can do this by creating a `.env` file in the root directory of your project.

### Example `.env` File

```env
API_BASE_URL=https://api.example.com
REFRESH_TOKEN=your-refresh-token
BACKEND=httpx
TTL_SECONDS=20
```

#### Variables:

- **`API_BASE_URL`**: The base URL of the Offers API.

- **`REFRESH_TOKEN`**: The refresh token used for authentication.

- **`BACKEND`**: The HTTP client to use, such as `httpx`, `aiohttp`, or `requests`.

- **`TTL_SECONDS`**: The time-to-live in seconds for cached offer data.

The `.env` file ensures that the SDK can read the required configuration settings and authenticate correctly when running the CLI commands.

## Commands

### `register-product`

This command allows you to register a new product with the Offers API.

```bash
poetry run offers-cli register-product "product-uuid" "Product Name" "Product Description"
```

#### Parameters:

- **`product-uuid`**: The unique identifier for the product (must be a valid UUID).

- **`Product Name`**: The name of the product.

- **`Product Description`**: A description of the product.

#### Example:

```bash
poetry run offers-cli register-product "3fa25f34-5937-4366-b4f9-2c963f17af61" "Smart TV" "A high-definition Smart TV"
```

### `get-offers`

This command retrieves offers associated with a specific product by its UUID.

```bash
poetry run offers-cli get-offers "product-uuid"
```

#### Parameters:

- **`product-uuid`**: The unique identifier for the product (must be a valid UUID).

#### Example:

```bash
poetry run offers-cli get-offers "1fa25f14-5117-4111-b4f1-1c167f12af61"
```

#### Output:

The available offers for the product will be displayed in a tabular format, including:

- Offer ID

- Price

- Stock

## How Does the CLI Handle Authentication?

The CLI uses a special `CachedAuthClient` class, which is designed to automatically manage and cache the authentication `access_token`. This ensures that:

- Your token doesn't expire during testing sessions.

- Unnecessary re-authentication is avoided.

### Key Features:

- The `access_token` is cached to a local file.

- The client will automatically load the token if it is available and valid.

- If the token is expired or missing, it will be refreshed automatically.

This behavior is transparent to the user and provides a smoother testing experience.

## Summary

The CLI tool provided with the Offers SDK is an excellent way to quickly interact with the Offers API, whether you're testing, debugging, or exploring the SDK's features. With the built-in authentication and simple commands, it allows you to easily register products and retrieve offers, all from the command line.

For more advanced CLI functionality, you can modify the commands or even extend the functionality by adding more operations to the CLI.