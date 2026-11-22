"""Model access. Providers come from TradingAgents' client factory, so switching
from a free development model to Claude is a config change only.

``FallbackChat`` tries several models in order and moves to the next one only
on a temporary provider problem (overload, timeout, rate or quota limit).
Real errors, such as a bad request, are raised at once rather than hidden.

Every call goes through ``Caller``, which records role, the model that
actually answered, latency and token use, for traceability and for the
cost/latency part of the evaluation.
"""

from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from langchain_core.messages import BaseMessage
from pydantic import BaseModel


def make_chat_model(provider: str, model: str, base_url: str | None = None, **kwargs) -> Any:
    """Build a LangChain chat model, e.g. ('anthropic', 'claude-sonnet-5-5') or ('google', 'gemini-...')."""
    from tradingagents.llm_clients import create_llm_client

    return create_llm_client(provider, model, base_url, **kwargs).get_llm()


# ---------------------------------------------------------------- fallback

_TRANSIENT = re.compile(
    r"RateLimit|RESOURCE_EXHAUSTED|\b429\b|\b503\b|\b504\b|\b502\b|UNAVAILABLE|DEADLINE_EXCEEDED|"
    r"overloaded|high demand|Timeout|timed out", re.I)


def is_transient(exc: BaseException) -> bool:
    """A temporary provider problem worth trying another model for (or stopping on), not a real error."""
    return isinstance(exc, TimeoutError) or bool(_TRANSIENT.search(f"{type(exc).__name__} {exc}"))


def parse_model_spec(spec: str) -> tuple[str, str]:
    """'openrouter:nvidia/nemotron-3.5-super-vl:free' -> ('openrouter', 'nvidia/nemotron-3.5-super-vl:free')."""
    provider, sep, model = spec.partition(":")
    if not sep or not provider or not model:
        raise ValueError(f"model spec {spec!r} must look like 'provider:model'")
    return provider, model


class FallbackChat:
    """Chat model that tries each (label, model) in order on temporary provider errors."""

    def __init__(self, models: list[tuple[str, Any]]):
        if not models:
            raise ValueError("FallbackChat needs at least one model")
        self.models = models
        self.last_used: str | None = None
        self.last_skipped: list[str] = []

    def _run(self, call):
        self.last_used, self.last_skipped = None, []
        error = None
        for label, model in self.models:
            try:
                out = call(model)
                self.last_used = label
                return out
            except Exception as exc:
                if not is_transient(exc):
                    raise
                error = exc
                self.last_skipped.append(f"{label}: {type(exc).__name__}")
        raise error

    def invoke(self, messages):
        return self._run(lambda m: m.invoke(messages))

    def with_structured_output(self, schema, **kwargs):
        chat = self

        class _Structured:
            def invoke(self, messages):
                return chat._run(lambda m: m.with_structured_output(schema, **kwargs).invoke(messages))
        return _Structured()


def make_fallback_chat(specs: list[str], base_url: str | None = None, **kwargs) -> FallbackChat:
    """Models in order of preference, e.g. ['google:gemini-4-hydrogen', 'openrouter:nvidia/...:free'].

    With more than one model, each gets few retries so an overloaded provider is
    skipped quickly instead of being retried for minutes.
    """
    if len(specs) > 1:
        kwargs = {"max_retries": 1, "timeout": 180, **kwargs}
    return FallbackChat([(s, make_chat_model(*parse_model_spec(s), base_url, **kwargs)) for s in specs])


# ---------------------------------------------------------------- call log


@dataclass
class CallRecord:
    role: str
    seconds: float
    input_tokens: int | None
    output_tokens: int | None
    error: str | None = None
    model: str | None = None            # which model answered (with FallbackChat)
    fallbacks: list[str] = field(default_factory=list)  # models skipped before it, and why


@dataclass
class Caller:
    llm: Any
    calls: list[CallRecord] = field(default_factory=list)

    def _record(self, role, start, msg, error=None):
        usage = getattr(msg, "usage_metadata", None) or {}
        self.calls.append(CallRecord(
            role, round(time.perf_counter() - start, 3), usage.get("input_tokens"), usage.get("output_tokens"),
            error, getattr(self.llm, "last_used", None), list(getattr(self.llm, "last_skipped", []))))

    def text(self, role: str, messages: list[BaseMessage]) -> str:
        start = time.perf_counter()
        msg = self.llm.invoke(messages)
        self._record(role, start, msg)
        content = msg.content
        if isinstance(content, list):  # some providers return content blocks
            content = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
        return content

    def structured(self, role: str, messages: list[BaseMessage], schema: type[BaseModel]) -> BaseModel:
        start = time.perf_counter()
        out = self.llm.with_structured_output(schema, include_raw=True).invoke(messages)
        error = out.get("parsing_error")
        detail = None
        if error or out.get("parsed") is None:
            raw = out.get("raw")
            raw_text = getattr(raw, "tool_calls", None) or getattr(raw, "content", None) or raw
            detail = f"{error!r} | raw output: {str(raw_text)[:4000]}"
        self._record(role, start, out.get("raw"), detail)
        if out.get("parsed") is None:
            raise ValueError(f"{role}: model output did not match {schema.__name__}: {error!r}")
        return out["parsed"]

    def log(self) -> list[dict]:
        return [asdict(c) for c in self.calls]
