# Offers API Python SDK

Welcome to the **Offers API Python SDK** documentation! This SDK allows developers to easily integrate with the Offers microservice to register products and retrieve offers.

## Documentations

- [Quickstart Guide](docs/quickstart.md)

- [API Reference](docs/api_reference.md)

- [Configuration](docs/configuration.md)

- [Plugins](docs/plugins.md)

- [Middleware Hooks](docs/hooks.md)

- [CLI Usage](docs/cli_usage.md)

## Overview

The Offers API Python SDK provides a simple interface to interact with our offers platform. With this SDK, you can:

- Register new products

- Fetch offers associated with specific products

- Handle authentication via refresh tokens

- Customize request/response processing with plugins

- Select between multiple HTTP clients (httpx, requests, aiohttp)

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
pip install .
```

## Quickstart Guide

Start with the [Quickstart Guide](quickstart.md) to get a product up and running in minutes.

## License

This SDK is open-source and available under the MIT License. See LICENSE for details.
