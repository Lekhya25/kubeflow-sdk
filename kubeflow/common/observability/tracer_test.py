from kubeflow.common.observability.config import ENABLE_OBSERVABILITY, get_tracer
from kubeflow.common.observability.tracer import BaseSpan, NoOpSpan, NoOpTracer


def test_get_tracer_returns_noop_tracer_by_default() -> None:
    tracer = get_tracer()
    assert ENABLE_OBSERVABILITY is False
    assert isinstance(tracer, NoOpTracer)


def test_noop_span_context_manager() -> None:
    span = NoOpSpan()

    with span as entered_span:
        assert entered_span is span


def test_noop_tracer_start_span_returns_noop_span() -> None:
    tracer = NoOpTracer()

    with tracer.start_span("trainer.train") as span:
        assert isinstance(span, BaseSpan)
        assert isinstance(span, NoOpSpan)


def test_noop_span_does_not_swallow_exceptions() -> None:
    span = NoOpSpan()

    try:
        with span:
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    else:
        raise AssertionError("NoOpSpan must not suppress exceptions")