# Observability PoC

This folder contains a minimal Proof of Concept for tracing in the Kubeflow SDK using a pluggable observability layer.

## What this PoC includes

- A minimal tracer abstraction
- A no-op tracer as the default
- An OpenTelemetry tracer with console span export
- Runtime tracer selection via configuration
- Instrumentation of one SDK client operation: TrainerClient.train

## Design goals

- Keep integration minimal and non-intrusive
- Preserve existing client behavior
- Add near-zero overhead when observability is disabled
- Demonstrate a clean extension path to broader instrumentation

## Components

- `tracer.py`
  - BaseTracer interface
  - BaseSpan interface
  - NoOpTracer and NoOpSpan

- `config.py`
  - ENABLE_OBSERVABILITY toggle
  - get_tracer helper for runtime tracer selection

- `otel_tracer.py`
  - OTelTracer implementation
  - Console exporter setup
  - Span error recording on exceptions

- `__init__.py`
  - Public exports for observability module types and helpers

## How tracing is selected

Tracing is controlled by environment variable KUBEFLOW_ENABLE_OBSERVABILITY.

Enabled values:
- 1
- true
- yes
- on

Any other value, or no value, uses the no-op tracer.

## Behavior summary

When disabled:
- NoOpTracer is used
- No spans are exported
- Existing SDK behavior is unchanged

When enabled:
- OTelTracer is used
- Span data is printed to console by OpenTelemetry ConsoleSpanExporter
- Exceptions inside instrumented spans are recorded on spans

## Current instrumentation scope

This PoC currently instruments:
- TrainerClient.train

Span name used:
- trainer.train

## Quick verification

Run the demo without tracing:

    python examples/observability_demo.py

Run the demo with tracing enabled in PowerShell:

    $env:KUBEFLOW_ENABLE_OBSERVABILITY='true'
    python examples/observability_demo.py
    Remove-Item Env:\KUBEFLOW_ENABLE_OBSERVABILITY

Expected result:
- Disabled run prints normal demo output with no span JSON
- Enabled run prints trainer.train span JSON to console

## Notes and limitations

- Console exporter is used for demonstration only
- Exporter, sampling, and resource configuration are intentionally basic

## Future extension path

This structure can be extended to:
- Instrument additional client methods
- Add trace attributes for richer context
- Add production exporters and config options
- Add metrics and logging with the same pluggable approach
