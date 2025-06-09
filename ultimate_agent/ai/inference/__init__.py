#!/usr/bin/env python3
"""
ultimate_agent/ai/inference/__init__.py
Hybrid inference engine with optional Advanced Ollama backend.

This module exposes :class:`HybridInferenceEngine` which prefers the real
Ollama backend when available and falls back to a lightweight mock
implementation.  ``InferenceEngine`` is kept as an alias for backwards
compatibility.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from collections import deque
from typing import Any, Dict, List, Optional

try:
    # Heavyweight backend providing real model execution.
    from ..backends.ollama_advanced import (
        AdvancedOllamaManager,
        InferenceRequest,
        OllamaInstance,
    )

    OLLAMA_AVAILABLE = True
except Exception as e:  # pragma: no cover - optional dependency
    logging.warning("Advanced Ollama backend unavailable: %s", e)
    OLLAMA_AVAILABLE = False
    AdvancedOllamaManager = None  # type: ignore
    InferenceRequest = None  # type: ignore
    OllamaInstance = None  # type: ignore


class HybridInferenceEngine:
    """Inference engine that optionally uses Advanced Ollama."""

    def __init__(self, ai_manager: Any) -> None:
        self.ai_manager = ai_manager
        self.config = getattr(ai_manager, "config", None)

        self.ollama_manager: Optional[AdvancedOllamaManager] = None
        self.ollama_available = OLLAMA_AVAILABLE
        self.ollama_initialized = False
        self.enable_fallback = True

        self.inference_cache: Dict[str, Dict[str, Any]] = {}
        self.inference_history: deque = deque(maxlen=1000)
        self.stats = {
            "total": 0,
            "success": 0,
            "ollama": 0,
            "fallback": 0,
            "cache_hits": 0,
            "total_time": 0.0,
        }

        if self.ollama_available:
            self._init_ollama()

    # ------------------------------------------------------------------
    # Ollama management
    # ------------------------------------------------------------------
    def _init_ollama(self) -> None:
        """Create and configure :class:`AdvancedOllamaManager`."""
        try:
            self.ollama_manager = AdvancedOllamaManager(self.config)
            if self.config:
                instances = self.config.get("OLLAMA", "instances", fallback="localhost:11434")
                for host in instances.split(","):
                    if ":" in host:
                        h, p = host.split(":", 1)
                        self.ollama_manager.add_instance(OllamaInstance(host=h.strip(), port=int(p)))
                    else:
                        self.ollama_manager.add_instance(OllamaInstance(host=host.strip()))
                self.enable_fallback = self.config.getboolean("OLLAMA", "enable_fallback", fallback=True)
            else:
                self.ollama_manager.add_instance(OllamaInstance(host="localhost"))
        except Exception as exc:  # pragma: no cover - runtime protection
            logging.warning("Failed to initialise Ollama manager: %s", exc)
            self.ollama_available = False

    async def _ensure_ollama_started(self) -> bool:
        if not self.ollama_available or not self.ollama_manager:
            return False
        if not self.ollama_initialized:
            try:
                await self.ollama_manager.start()
                self.ollama_initialized = True
            except Exception as exc:  # pragma: no cover - runtime protection
                logging.warning("Failed to start Ollama manager: %s", exc)
                if not self.enable_fallback:
                    raise
                return False
        return True

    async def _ollama_inference(self, model: str, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        await self._ensure_ollama_started()
        assert self.ollama_manager and InferenceRequest
        request = InferenceRequest(model=model, prompt=prompt, options=kwargs.get("options", {}))
        response = await self.ollama_manager.generate(request)
        return {
            "success": response.success,
            "prediction": response.response if response.success else None,
            "error": response.error if not response.success else None,
            "model_name": model,
            "processing_time": response.processing_time,
            "tokens_per_second": response.tokens_per_second,
            "real_inference": True,
        }

    # ------------------------------------------------------------------
    # Mock fallback implementation
    # ------------------------------------------------------------------
    async def _mock_inference(self, model: str, prompt: str) -> Dict[str, Any]:
        await asyncio.sleep(0)  # allow scheduling
        processing_time = random.uniform(0.1, 0.5)
        await asyncio.sleep(min(processing_time, 0.2))
        response = f"Processed '{prompt[:50]}...' with {model} (mock)"
        return {
            "success": True,
            "prediction": response,
            "confidence": random.uniform(0.7, 0.9),
            "model_name": model,
            "processing_time": processing_time,
            "real_inference": False,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def run_inference(self, model_name: str, input_data: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute inference using Ollama or mock fallback."""
        self.stats["total"] += 1
        start = time.time()
        prompt = str(input_data)
        cache_key = f"{model_name}:{prompt}"[:256]

        if cache_key in self.inference_cache:
            self.stats["cache_hits"] += 1
            result = self.inference_cache[cache_key].copy()
            result["cached"] = True
            return result

        if self.ollama_available:
            try:
                result = await self._ollama_inference(model_name, prompt, **kwargs)
                if result.get("success"):
                    self.stats["ollama"] += 1
                    self.stats["success"] += 1
                else:
                    if not self.enable_fallback:
                        self._record_stats(result, time.time() - start)
                        return result
                    result = await self._mock_inference(model_name, prompt)
            except Exception as exc:  # pragma: no cover - runtime protection
                logging.warning("Ollama inference failed: %s", exc)
                if not self.enable_fallback:
                    raise
                result = await self._mock_inference(model_name, prompt)
        else:
            result = await self._mock_inference(model_name, prompt)

        if result.get("success"):
            self.stats["success"] += 1
        else:
            self.stats["fallback"] += 1
        self._record_stats(result, time.time() - start)
        self.inference_cache[cache_key] = result.copy()
        self.inference_history.appendleft({"model": model_name, "prompt": prompt, "result": result})
        result["cached"] = False
        return result

    def _record_stats(self, result: Dict[str, Any], duration: float) -> None:
        self.stats["total_time"] += duration

    async def list_models(self) -> List[str]:
        if self.ollama_available and await self._ensure_ollama_started():
            try:
                models = await self.ollama_manager.get_available_models()
                return list(models)
            except Exception as exc:  # pragma: no cover - runtime protection
                logging.warning("Failed to list Ollama models: %s", exc)
        return []

    def get_performance_stats(self) -> Dict[str, Any]:
        total = max(self.stats["total"], 1)
        return {
            "total_inferences": self.stats["total"],
            "success_rate": self.stats["success"] / total,
            "ollama_usage_rate": self.stats["ollama"] / total,
            "fallback_usage_rate": self.stats["fallback"] / total,
            "cache_hit_rate": self.stats["cache_hits"] / total,
            "average_inference_time": self.stats["total_time"] / total,
        }

    def clear_cache(self) -> None:
        self.inference_cache.clear()

    async def close(self) -> None:
        if self.ollama_manager and self.ollama_initialized:
            await self.ollama_manager.stop()
            self.ollama_initialized = False


# Backwards compatibility -------------------------------------------------------
InferenceEngine = HybridInferenceEngine

def create_inference_engine(ai_manager: Any) -> HybridInferenceEngine:
    """Factory used by older code."""
    return HybridInferenceEngine(ai_manager)
