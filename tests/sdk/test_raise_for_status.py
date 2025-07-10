import pytest
from sdk.utils.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    OffersAPIError,
    RateLimitError,
    ServerError,
    TimeoutError,
)
from sdk.http.utils import raise_for_status_with_text


class DummyResponse:
    def __init__(self, status_code: int, text: str = "error text"):
        self.status_code = status_code
        self.text = text


@pytest.mark.parametrize("code,expected_exception", [
    (401, AuthenticationError),
    (404, NotFoundError),
    (409, ConflictError),
    (429, RateLimitError),
    (408, TimeoutError),
    (500, ServerError),
    (502, ServerError),
    (400, OffersAPIError),
    (422, OffersAPIError),
])
def test_raise_for_status_with_text_raises_exceptions(code, expected_exception):
    response = DummyResponse(status_code=code, text="error text")
    with pytest.raises(expected_exception) as exc_info:
        raise_for_status_with_text(response)
    assert "error text" in str(exc_info.value)


def test_raise_for_status_with_text_passes_on_200():
    response = DummyResponse(status_code=200, text="ok")
    assert raise_for_status_with_text(response) is None


def test_raise_for_status_with_text_passes_on_204():
    response = DummyResponse(status_code=204, text="no content")
    assert raise_for_status_with_text(response) is None


def test_raise_for_status_with_text_passes_on_302():
    response = DummyResponse(status_code=302, text="redirect")
    assert raise_for_status_with_text(response) is None
