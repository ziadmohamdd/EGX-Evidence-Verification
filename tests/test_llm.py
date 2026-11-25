"""Provider fallback: no network, scripted models."""

import pytest
from langchain_core.messages import AIMessage
from pydantic import BaseModel

from egx_guide.llm import Caller, FallbackChat, is_transient, parse_model_spec


class ServerError(Exception):
    pass


class Model:
    def __init__(self, name, fail=None):
        self.name, self.fail, self.calls = name, fail, 0

    def invoke(self, messages):
        self.calls += 1
        if self.fail:
            raise self.fail
        return AIMessage(f"from {self.name}", usage_metadata={"input_tokens": 1, "output_tokens": 2, "total_tokens": 3})

    def with_structured_output(self, schema, include_raw=False, **kw):
        outer = self
        self.structured_kw = kw

        class Runnable:
            def invoke(self, messages):
                msg = outer.invoke(messages)
                return {"raw": msg, "parsed": schema(answer=msg.content), "parsing_error": None}
        return Runnable()


class Answer(BaseModel):
    answer: str


@pytest.mark.parametrize("exc, transient", [
    (ServerError("503 UNAVAILABLE. This model is currently experiencing high demand"), True),
    (ServerError("504 DEADLINE_EXCEEDED"), True),
    (ServerError("429 RESOURCE_EXHAUSTED"), True),
    (type("OpenAIRateLimitError", (Exception,), {})("Error code: 429"), True),
    (TimeoutError("timed out"), True),
    (ValueError("model output did not match"), False),
    (ServerError("400 INVALID_ARGUMENT"), False),
])
def test_transient_errors(exc, transient):
    assert is_transient(exc) is transient


def test_falls_back_on_overload_and_records_which_model_answered():
    down = Model("gemini", ServerError("503 UNAVAILABLE"))
    up = Model("nemotron")
    caller = Caller(FallbackChat([("google:gemini", down), ("openrouter:nemotron", up)]))
    assert caller.text("t", []) == "from nemotron"
    assert caller.log()[0]["model"] == "openrouter:nemotron"
    assert caller.log()[0]["fallbacks"] == ["google:gemini: ServerError"]


def test_structured_output_falls_back_too():
    caller = Caller(FallbackChat([("a", Model("a", ServerError("429 RESOURCE_EXHAUSTED"))), ("b", Model("b"))]))
    assert caller.structured("s", [], Answer).answer == "from b"
    assert caller.log()[0]["model"] == "b"


def test_primary_is_used_when_it_works():
    a, b = Model("a"), Model("b")
    caller = Caller(FallbackChat([("a", a), ("b", b)]))
    caller.text("t", [])
    assert a.calls == 1 and b.calls == 0 and caller.log()[0]["model"] == "a"


def test_real_errors_are_not_hidden_by_fallback():
    b = Model("b")
    with pytest.raises(ServerError, match="400"):
        FallbackChat([("a", Model("a", ServerError("400 INVALID_ARGUMENT"))), ("b", b)]).invoke([])
    assert b.calls == 0


def test_all_down_raises_the_last_error():
    chat = FallbackChat([("a", Model("a", ServerError("503 UNAVAILABLE"))),
                         ("b", Model("b", ServerError("429 RESOURCE_EXHAUSTED")))])
    with pytest.raises(ServerError, match="429"):
        chat.invoke([])


def test_parse_model_spec_keeps_colons_in_model_names():
    assert parse_model_spec("openrouter:nvidia/nemotron-3.5-super-vl:free") == ("openrouter", "nvidia/nemotron-3.5-super-vl:free")
    with pytest.raises(ValueError):
        parse_model_spec("no-provider")


def test_nvidia_uses_json_schema_output_other_providers_keep_the_default():
    # NVIDIA's function-calling mode cuts string fields at 1,024 characters
    nv, g = Model("nv"), Model("g")
    Caller(FallbackChat([("nvidia:nemotron", nv)])).structured("s", [], Answer)
    Caller(FallbackChat([("google:gemini", g)])).structured("s", [], Answer)
    assert nv.structured_kw == {"method": "json_schema"}
    assert g.structured_kw == {}
