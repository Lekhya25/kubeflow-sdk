# Copyright 2025 The Kubeflow Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Unit tests for TrainerClient backend selection.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from kubeflow.common.types import KubernetesBackendConfig
from kubeflow.trainer.api.trainer_client import TrainerClient
from kubeflow.trainer.backends.localprocess.types import LocalProcessBackendConfig


@pytest.mark.parametrize(
    "test_case",
    [
        {
            "name": "default_backend_is_kubernetes",
            "backend_config": None,
            "expected_backend": "KubernetesBackend",
            "use_k8s_mocks": True,
        },
        {
            "name": "local_process_backend_selection",
            "backend_config": LocalProcessBackendConfig(),
            "expected_backend": "LocalProcessBackend",
            "use_k8s_mocks": False,
        },
        {
            "name": "kubernetes_backend_selection",
            "backend_config": KubernetesBackendConfig(),
            "expected_backend": "KubernetesBackend",
            "use_k8s_mocks": True,
        },
    ],
)
def test_backend_selection(test_case):
    """Test TrainerClient backend selection logic."""
    if test_case["use_k8s_mocks"]:
        with (
            patch("kubernetes.config.load_kube_config"),
            patch("kubernetes.client.CustomObjectsApi") as mock_custom_api,
            patch("kubernetes.client.CoreV1Api") as mock_core_api,
        ):
            mock_custom_api.return_value = Mock()
            mock_core_api.return_value = Mock()

            if test_case["backend_config"]:
                client = TrainerClient(backend_config=test_case["backend_config"])
            else:
                client = TrainerClient()

            backend_name = client.backend.__class__.__name__
            assert backend_name == test_case["expected_backend"]
    else:
        client = TrainerClient(backend_config=test_case["backend_config"])
        backend_name = client.backend.__class__.__name__
        assert backend_name == test_case["expected_backend"]

def test_train_wraps_backend_call_in_span() -> None:
    mock_backend = Mock()
    mock_backend.train.return_value = "job-1"
    mock_span = MagicMock()
    mock_span.__enter__.return_value = mock_span
    mock_span.__exit__.return_value = False

    mock_tracer = Mock()
    mock_tracer.start_span.return_value = mock_span

    client = TrainerClient(backend_config=LocalProcessBackendConfig())
    client.backend = mock_backend

    with patch("kubeflow.trainer.api.trainer_client.get_tracer", return_value=mock_tracer):
        result = client.train(runtime="test-runtime")

    assert result == "job-1"
    mock_tracer.start_span.assert_called_once_with("trainer.train")
    mock_backend.train.assert_called_once_with(
        runtime="test-runtime",
        initializer=None,
        trainer=None,
        options=None,
    )
    mock_span.__enter__.assert_called_once()
    mock_span.__exit__.assert_called_once()

def test_train_propagates_backend_exceptions() -> None:
    mock_backend = Mock()
    mock_backend.train.side_effect = RuntimeError("backend failure")
    mock_span = MagicMock()
    mock_span.__enter__.return_value = mock_span
    mock_span.__exit__.return_value = False

    mock_tracer = Mock()
    mock_tracer.start_span.return_value = mock_span

    client = TrainerClient(backend_config=LocalProcessBackendConfig())
    client.backend = mock_backend

    with patch("kubeflow.trainer.api.trainer_client.get_tracer", return_value=mock_tracer):
        with pytest.raises(RuntimeError, match="backend failure"):
            client.train()

    mock_tracer.start_span.assert_called_once_with("trainer.train")
    mock_backend.train.assert_called_once_with(
        runtime=None,
        initializer=None,
        trainer=None,
        options=None,
    )
    mock_span.__enter__.assert_called_once()
    mock_span.__exit__.assert_called_once()
