"""LLM backend adapters.

Current adapters:
  - AnthropicAdapter: Claude (Sonnet / Haiku / Opus)
  - DeterministicStubAdapter: offline replacement that returns plausible
    JSON responses for pipeline tests and for dry runs without an API key.
"""

from __future__ import annotations

import json
import os
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

try:  # optional dependency
    import anthropic  # type: ignore
except Exception:  # pragma: no cover
    anthropic = None  # type: ignore


@dataclass
class LLMResponse:
    text: str
    backend: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class LLMAdapter(ABC):
    @abstractmethod
    def complete(self, prompt: str, *, max_output_tokens: int = 3000) -> LLMResponse:
        ...


class AnthropicAdapter(LLMAdapter):
    def __init__(self, model: str = "claude-sonnet-4-6",
                 api_key: str | None = None) -> None:
        if anthropic is None:
            raise RuntimeError(
                "anthropic SDK not installed. `pip install anthropic --break-system-packages`"
            )
        self.model = model
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )

    def complete(self, prompt: str, *, max_output_tokens: int = 8000) -> LLMResponse:
        start = time.perf_counter()
        # Retry on transient server errors with exponential backoff.
        transient_codes = {429, 500, 502, 503, 529}
        max_attempts = 6
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_output_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                break
            except Exception as e:
                status = getattr(e, "status_code", None)
                is_transient = status in transient_codes or "overloaded" in str(e).lower()
                if not is_transient or attempt >= max_attempts:
                    raise
                # Exponential backoff with jitter: 4s, 8s, 16s, 32s, 64s, 128s
                delay = min(128, 2 ** (attempt + 1))
                print(f"[AnthropicAdapter] transient error (status={status}); "
                      f"retry {attempt}/{max_attempts} in {delay}s: {e}")
                time.sleep(delay)
        latency_ms = int((time.perf_counter() - start) * 1000)
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", "") == "text"
        )
        return LLMResponse(
            text=text,
            backend="anthropic",
            model=self.model,
            input_tokens=getattr(resp.usage, "input_tokens", 0),
            output_tokens=getattr(resp.usage, "output_tokens", 0),
            latency_ms=latency_ms,
            metadata={"stop_reason": getattr(resp, "stop_reason", None)},
        )


class DeterministicStubAdapter(LLMAdapter):
    """Deterministic stub for offline / CI runs.

    Produces a plausible RAITG-style JSON response for the requirement
    identified in the prompt. Does NOT call any external service.
    """

    def __init__(self, quality: float = 0.80) -> None:
        self.quality = quality
        self._rng = random.Random(42)

    def complete(self, prompt: str, *, max_output_tokens: int = 3000) -> LLMResponse:
        # Pull the requirement id out of the prompt
        req_id = "R-UNKNOWN"
        for line in prompt.splitlines():
            if line.startswith("Requirement ID:"):
                req_id = line.split(":", 1)[1].strip()
                break
        # "naive" mode uses plain text; here we always emit JSON
        is_naive = "[OUTPUT]" not in prompt
        if is_naive:
            body = (
                f"# tests for {req_id}\n"
                "def test_positive(): assert True\n"
                "def test_negative(): assert True\n"
                "def test_boundary(): assert True\n"
            )
            return LLMResponse(text=body, backend="stub", model="stub-naive",
                               input_tokens=len(prompt) // 4,
                               output_tokens=len(body) // 4,
                               latency_ms=10)

        # Occasionally drop a required field to simulate imperfect output
        drop_trace = self._rng.random() > self.quality

        tests = []
        for kind, heur in [("positive", "EP"), ("negative", "NEG"), ("boundary", "BVA")]:
            test = {
                "name": f"{kind}_case_{req_id}",
                "kind": kind,
                "heuristic": heur,
                "preconditions": ["system under test is available"],
                "actions": [f"invoke requirement {req_id} in {kind} mode"],
                "expected": [
                    "successful response" if kind == "positive" else "documented error"
                ],
                "trace": [] if drop_trace else [req_id],
                "executable": (
                    f"def test_{kind}_{req_id.replace('-','_').lower()}():\n"
                    f"    # stub test\n    assert True\n"
                ),
            }
            tests.append(test)

        doc = {
            "requirement_id": req_id,
            "reasoning": f"Applied heuristics to {req_id}.",
            "tests": tests,
        }
        text = json.dumps(doc)
        return LLMResponse(text=text, backend="stub", model="stub-raitg",
                           input_tokens=len(prompt) // 4,
                           output_tokens=len(text) // 4,
                           latency_ms=15)


def build_adapter(backend: str = "auto",
                  model: str = "claude-sonnet-4-6") -> LLMAdapter:
    backend = backend.lower()
    if backend == "stub":
        return DeterministicStubAdapter()
    if backend == "stdlib":
        from llm_adapter_stdlib import StdlibAnthropicAdapter  # type: ignore
        return StdlibAnthropicAdapter(model=model)  # type: ignore[return-value]
    if backend in ("auto", "anthropic", "claude"):
        has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
        has_sdk = anthropic is not None
        if has_key and has_sdk:
            return AnthropicAdapter(model=model)
        if has_key and not has_sdk:
            from llm_adapter_stdlib import StdlibAnthropicAdapter  # type: ignore
            print("[llm_adapter] anthropic SDK absent — using stdlib adapter")
            return StdlibAnthropicAdapter(model=model)  # type: ignore[return-value]
        if backend == "auto":
            reason = []
            if not has_key: reason.append("ANTHROPIC_API_KEY not set")
            if not has_sdk: reason.append("anthropic SDK not installed")
            print(f"[llm_adapter] {'; '.join(reason)} — falling back to stub")
            return DeterministicStubAdapter()
        # Explicit backend request: be specific about what's missing
        problems = []
        if not has_key:
            problems.append(
                "ANTHROPIC_API_KEY env var is not set. "
                "Set it with: $env:ANTHROPIC_API_KEY='sk-ant-...' (PowerShell)"
            )
        if not has_sdk:
            problems.append(
                "anthropic SDK is not installed. "
                "Install it with: pip install anthropic"
            )
        raise RuntimeError(
            "Anthropic backend requested but unavailable:\n  - "
            + "\n  - ".join(problems)
        )
    raise ValueError(f"unknown backend: {backend}")
