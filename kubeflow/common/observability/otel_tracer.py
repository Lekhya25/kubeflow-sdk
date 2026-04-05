from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from kubeflow.common.observability.tracer import BaseSpan, BaseTracer


@dataclass
class OTelSpan(BaseSpan):
    # Adapter that exposes an OpenTelemetry span as a context manager.

    span: trace.Span

    def __enter__(self) -> OTelSpan:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback,
    ) -> bool:
        if exc_type is not None:
            self.span.record_exception(exc_value)
            self.span.set_status(trace.Status(trace.StatusCode.ERROR))
        self.span.end()
        return False


class OTelTracer(BaseTracer):
    # OpenTelemetry-based tracer with console export.

    def __init__(self, service_name: str = "kubeflow-sdk") -> None:
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)
        self._tracer = trace.get_tracer(service_name)

    def start_span(self, name: str) -> BaseSpan:
        span = self._tracer.start_span(name)
        return OTelSpan(span=span)