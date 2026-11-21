"""Model access. Providers come from TradingAgents' client factory, so switching
from a free development model to Claude is a config change only.

Every call goes through ``Caller``, which records role, latency and token use
for the cost/latency part of the evaluation.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any

from langchain_core.messages import BaseMessage
from pydantic import BaseModel


def make_chat_model(provider: str, model: str, base_url: str | None = None, **kwargs) -> Any:
    """Build a LangChain chat model, e.g. ('anthropic', 'claude-sonnet-5-5') or ('google', 'gemini-...')."""
    from tradingagents.llm_clients import create_llm_client

    return create_llm_client(provider, model, base_url, **kwargs).get_llm()


@dataclass
class CallRecord:
    role: str
    seconds: float
    input_tokens: int | None
    output_tokens: int | None
    error: str | None = None


@dataclass
class Caller:
    llm: Any
    calls: list[CallRecord] = field(default_factory=list)

    def _record(self, role, start, msg, error=None):
        usage = getattr(msg, "usage_metadata", None) or {}
        self.calls.append(CallRecord(role, round(time.perf_counter() - start, 3),
                                     usage.get("input_tokens"), usage.get("output_tokens"), error))

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
        self._record(role, start, out.get("raw"), repr(error) if error else None)
        if out.get("parsed") is None:
            raise ValueError(f"{role}: model output did not match {schema.__name__}: {error!r}")
        return out["parsed"]

    def log(self) -> list[dict]:
        return [asdict(c) for c in self.calls]
