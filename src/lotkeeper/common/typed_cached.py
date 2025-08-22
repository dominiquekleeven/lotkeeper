from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar, cast

from aiocache import cached as _aiocache_cached

P = ParamSpec("P")
R = TypeVar("R")


def typed_cached(
    *,
    ttl: int | float | None = None,
    key_builder: Callable[..., str] | None = None,
    **kwargs: Any,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """
    Typed wrapper around aiocache.cached that preserves the async signature.
    Use exactly like aiocache.cached(...).
    """
    dec = _aiocache_cached(ttl=ttl, key_builder=key_builder, **kwargs)
    return cast(Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]], dec)
