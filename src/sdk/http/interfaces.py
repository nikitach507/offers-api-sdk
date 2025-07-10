from typing import Any, Protocol


class BaseResponse(Protocol):
    @property
    def status_code(self) -> int:
        ...
    
    @property
    def text(self) -> str:
        ...
    
    async def json(self) -> Any:
        ...


class HTTPBackend(Protocol):
    async def request(self, method: str, url: str, **kwargs: Any) -> BaseResponse:
        ...

    async def aclose(self) -> None:
        ...
