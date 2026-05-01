"""Type stubs for okta.pagination — covers PaginationHelper + paginate_all."""

from collections.abc import AsyncIterator
from typing import Any, Awaitable, Callable, Dict, Optional

class PaginationHelper:
    @staticmethod
    def extract_next_cursor(headers: Dict[str, Any]) -> Optional[str]: ...
    @staticmethod
    def has_next_page(headers: Dict[str, Any]) -> bool: ...

def paginate_all(
    api_method: Callable[..., Awaitable[tuple[Any, Any, Any]]],
    limit: int = ...,
    max_pages: Optional[int] = ...,
    **kwargs: Any,
) -> AsyncIterator[Any]: ...
def paginate_pages(
    api_method: Callable[..., Awaitable[tuple[Any, Any, Any]]],
    limit: int = ...,
    max_pages: Optional[int] = ...,
    **kwargs: Any,
) -> AsyncIterator[list[Any]]: ...
