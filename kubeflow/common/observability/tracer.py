from __future__ import annotations

import abc
from types import TracebackType


class BaseSpan(abc.ABC):
    """Minimal span interface used by SDK clients."""

    @abc.abstractmethod
    def __enter__(self) -> BaseSpan:
        """Enter the span context."""
        raise NotImplementedError

    @abc.abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        """Exit the span context."""
        raise NotImplementedError


class NoOpSpan(BaseSpan):
    """Context manager that intentionally does nothing."""

    def __enter__(self) -> NoOpSpan:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        return False


class BaseTracer(abc.ABC):
    """Minimal tracer interface used by SDK clients."""

    @abc.abstractmethod
    def start_span(self, name: str) -> BaseSpan:
        """Start a span-like context manager."""
        raise NotImplementedError


class NoOpTracer(BaseTracer):
    """Default tracer when observability is disabled."""

    def start_span(self, name: str) -> BaseSpan:
        return NoOpSpan()