"""Utilities for privacy-preserving federated learning."""

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    class _DummyNumpy:
        class ndarray:
            pass

    np = _DummyNumpy()

from typing import Tuple

class SimpleEncryptor:
    """Lightweight additive encryption for simulation."""

    @staticmethod
    def generate_key(shape: Tuple[int, ...]) -> np.ndarray:
        return np.random.randn(*shape)

    @staticmethod
    def encrypt(data: np.ndarray, key: np.ndarray) -> np.ndarray:
        return data + key

    @staticmethod
    def decrypt(encrypted: np.ndarray, key: np.ndarray) -> np.ndarray:
        return encrypted - key
