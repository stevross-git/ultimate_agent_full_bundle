import importlib
import pytest
from ultimate_agent.ai.models.ai_models import AIModelManager

if importlib.util.find_spec('numpy') is None:
    pytest.skip("numpy not available", allow_module_level=True)

class DummyConfig:
    pass

def test_knowledge_distillation():
    manager = AIModelManager(DummyConfig())
    engine = manager.training_engine

    progress = []
    def cb(p, info):
        progress.append(p)
        return True

    result = engine.knowledge_distillation(
        {
            'epochs': 2,
            'temperature': 2.5,
            'alpha': 0.6,
            'method': 'soft',
            'mutual': True,
        },
        cb,
    )

    assert result['success'] is True
    assert result['epochs'] == 2
    assert result['distillation_method'] == 'soft'
    assert 'final_student_loss' in result
    assert 'final_teacher_loss' in result
    assert len(progress) == 2
