from __future__ import annotations

import os

from kubeflow.common.observability.tracer import BaseTracer, NoOpTracer

ENABLE_OBSERVABILITY = os.getenv("KUBEFLOW_ENABLE_OBSERVABILITY", "").lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def get_tracer() -> BaseTracer:
    """Return the active tracer implementation.

    The OpenTelemetry tracer is imported lazily so the disabled path stays cheap.
    """
    if not ENABLE_OBSERVABILITY:
        return NoOpTracer()

    from kubeflow.common.observability.otel_tracer import OTelTracer

    return OTelTracer()