import types
import importlib
import pytest
from ultimate_agent.ai.models.ai_models import AIModelManager

if importlib.util.find_spec('numpy') is None:
    pytest.skip("numpy not available", allow_module_level=True)

class DummyConfig:
    pass

def test_privacy_preserving_federated_learning():
    manager = AIModelManager(DummyConfig())
    engine = manager.training_engine

    progress_calls = []
    def cb(progress, info):
        progress_calls.append(progress)
        return True

    result = engine.federated_learning_step(
        {
            'num_clients': 3,
            'aggregation_rounds': 2,
            'differential_privacy': True,
            'encrypted_updates': True,
            'dp_noise_scale': 0.05,
        },
        cb
    )

    assert result['success'] is True
    assert result['differential_privacy'] is True
    assert result['encrypted_updates'] is True
    assert len(progress_calls) == 2


def test_ckks_encryption_scheme():
    manager = AIModelManager(DummyConfig())
    engine = manager.training_engine

    result = engine.federated_learning_step(
        {
            'num_clients': 2,
            'aggregation_rounds': 1,
            'encrypted_updates': True,
            'encryption_scheme': 'ckks',
        },
        lambda p, i: True,
    )

    assert result['success'] is True
    assert result['encrypted_updates'] is True
    assert result['encryption_scheme'] == 'ckks'
