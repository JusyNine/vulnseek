"""Built-in tools and their model-facing definitions."""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    invoke: Callable[[Any], dict[str, Any]]

    def definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


def count_words(arguments: Any) -> dict[str, int]:
    if (
        not isinstance(arguments, dict)
        or arguments.keys() != {"text"}
        or not isinstance(arguments["text"], str)
    ):
        raise ValueError("Expected an object containing a single string field named text.")
    return {"words": len(arguments["text"].split())}


WORD_COUNT = Tool(
    name="count_words",
    description="Count whitespace-separated words in supplied text.",
    parameters={
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
        "additionalProperties": False,
    },
    invoke=count_words,
)
