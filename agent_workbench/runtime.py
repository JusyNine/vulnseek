"""Run one conversation using a replaceable model and a fixed tool registry."""

import json
from typing import Any, Mapping, Protocol, Sequence

from .tools import Tool

Message = dict[str, Any]


class Model(Protocol):
    def respond(self, messages: Sequence[Message], tools: Sequence[Tool]) -> Message:
        ...


class AgentError(RuntimeError):
    pass


def run(
    prompt: str, model: Model, tools: Mapping[str, Tool], max_turns: int = 8
) -> str:
    messages = [
        {"role": "system", "content": "Answer the user in their language. Use tools when helpful."},
        {"role": "user", "content": prompt},
    ]
    for _ in range(max_turns):
        response = model.respond(messages, tuple(tools.values()))
        calls = response.get("tool_calls") or []
        if not calls:
            answer = response.get("content")
            if not isinstance(answer, str) or not answer.strip():
                raise AgentError("The model returned no answer.")
            return answer
        if len(calls) > 8:
            raise AgentError("The model exceeded the tool call limit for one turn.")
        messages.append(response)
        for call in calls:
            function = call["function"]
            tool = tools.get(function["name"])
            if tool is None:
                result = {"error": "Unknown tool"}
            else:
                try:
                    result = tool.invoke(json.loads(function["arguments"]))
                except ValueError as error:
                    result = {"error": str(error)}
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": json.dumps(result, ensure_ascii=False),
            })
    raise AgentError("The agent reached its model turn limit.")
