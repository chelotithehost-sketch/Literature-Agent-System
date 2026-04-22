# core/routing.py
from typing import List, Dict, Any, Optional
from loguru import logger
from core.llm_interface import LLMProvider
from core.memory import memory_pool
import random

class Router:
    """
    Mixture-of-Experts inspired routing layer.
    Routes tasks to appropriate LLM providers based on task type,
    current load, cost, and memory pressure.
    Implements bias adjustment to balance usage (avoid expert collapse).
    """
    def __init__(self, config: Dict[str, Any]):
        self.providers: Dict[str, LLMProvider] = {}
        for name, cfg in config["providers"].items():
            self.providers[name] = LLMProvider(cfg)
        self.routing_bias = {name: 0.0 for name in self.providers}
        self.usage_counts = {name: 0 for name in self.providers}

    def select_provider(self, task_type: str, priority: str = "cost") -> LLMProvider:
        """
        Select provider based on task type, current bias, and memory constraints.
        - task_type: "planning", "drafting", "review", "light"
        - priority: "cost", "speed", "quality"
        """
        candidates = []
        for name, provider in self.providers.items():
            # Filter by task type suitability (defined in config)
            if task_type in provider.config.get("suitable_for", []):
                candidates.append(name)

        if not candidates:
            candidates = list(self.providers.keys())

        # Apply routing bias (like MoE bias to balance usage)
        scores = {}
        for name in candidates:
            base = 1.0
            if priority == "cost":
                base = 1.0 / (provider.cost_per_1k + 0.001)
            elif priority == "speed":
                base = provider.config.get("speed_score", 1.0)
            elif priority == "quality":
                base = provider.config.get("quality_score", 1.0)
            # Add bias term to encourage underutilized providers
            scores[name] = base + self.routing_bias[name]

        # Softmax selection
        total = sum(scores.values())
        probs = [scores[n] / total for n in candidates]
        selected = random.choices(candidates, weights=probs, k=1)[0]

        # Update bias: decrease for selected, increase for others
        for name in self.routing_bias:
            if name == selected:
                self.routing_bias[name] -= 0.1
            else:
                self.routing_bias[name] += 0.05
        self.usage_counts[selected] += 1

        # Memory pressure override: if local Ollama is selected but memory > threshold, fallback to cloud
        if "ollama" in selected and memory_pool.check_memory_pressure():
            logger.warning("Memory pressure high, falling back to cloud provider")
            fallback = next((p for p in candidates if "cloud" in p), candidates[0])
            selected = fallback

        logger.info(f"Routing {task_type} to {selected} (priority: {priority})")
        return self.providers[selected]
