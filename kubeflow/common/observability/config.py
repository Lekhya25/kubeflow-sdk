from __future__ import annotations

from kubeflow.common.observability.tracer import BaseTracer, NoOpTracer

ENABLE_OBSERVABILITY = False


def get_tracer() -> BaseTracer:
    """Return the active tracer implementation.
    """
    return NoOpTracer()