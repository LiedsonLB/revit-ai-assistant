"""
Wrapper fino sobre o provider de LLM (Anthropic ou OpenAI), unificando a
interface de tool calling que o agent.py consome. Trocar de provider é
só mudar LLM_PROVIDER no .env — o resto do código não muda.
"""
from dataclasses import dataclass, field
from typing import Any

from ..config import settings


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict[str, Any]


@dataclass
class LLMResult:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop_reason: str = ""
    raw: Any = None


class LLMClient:
    def __init__(self):
        self.provider = settings.llm_provider

        if self.provider == "anthropic":
            import anthropic
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            self._model = settings.anthropic_model
        elif self.provider == "openai":
            import openai
            self._client = openai.OpenAI(api_key=settings.openai_api_key)
            self._model = settings.openai_model
        else:
            raise ValueError(f"LLM_PROVIDER inválido: {self.provider}")

    def call(
        self,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_tokens: int = 1500,
    ) -> LLMResult:
        if self.provider == "anthropic":
            return self._call_anthropic(system, messages, tools, max_tokens)
        return self._call_openai(system, messages, tools, max_tokens)

    # ── Anthropic ────────────────────────────────────────────────
    def _call_anthropic(self, system, messages, tools, max_tokens) -> LLMResult:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            tools=tools,
        )
        text_parts = []
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(id=block.id, name=block.name, input=block.input))

        return LLMResult(
            text="\n".join(text_parts),
            tool_calls=tool_calls,
            stop_reason=response.stop_reason,
            raw=response,
        )

    # ── OpenAI (function calling) ───────────────────────────────
    def _call_openai(self, system, messages, tools, max_tokens) -> LLMResult:
        oa_tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"],
                },
            }
            for t in tools
        ]
        oa_messages = [{"role": "system", "content": system}, *messages]

        response = self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=oa_messages,
            tools=oa_tools,
        )
        choice = response.choices[0]
        tool_calls = []
        if choice.message.tool_calls:
            import json
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        input=json.loads(tc.function.arguments or "{}"),
                    )
                )

        return LLMResult(
            text=choice.message.content or "",
            tool_calls=tool_calls,
            stop_reason=choice.finish_reason,
            raw=response,
        )
