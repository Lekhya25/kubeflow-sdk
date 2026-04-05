from __future__ import annotations

import os
from typing import Any

from kubeflow.trainer import LocalProcessBackendConfig, TrainerClient


class _DemoBackend:
    def train(
        self,
        runtime: Any = None,
        initializer: Any = None,
        trainer: Any = None,
        options: list | None = None,
    ) -> str:
        print("Demo backend train called")
        return "demo-train-job"

def _is_enabled() -> bool:
    return os.getenv("KUBEFLOW_ENABLE_OBSERVABILITY", "").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

def main() -> None:
    print("Starting observability demo")
    print(f"Observability enabled: {_is_enabled()}")

    client = TrainerClient(backend_config=LocalProcessBackendConfig())
    client.backend = _DemoBackend()

    job_name = client.train(runtime="torch-distributed")
    print(f"Train returned job name: {job_name}")
    print("If observability is enabled, span output is printed to console.")


if __name__ == "__main__":
    main()

