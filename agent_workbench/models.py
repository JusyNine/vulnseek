"""Offline demo and Chat Completions-compatible model adapters."""

import json
from typing import Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .runtime import AgentError, Message
from .tools import Tool


class DemoModel:
    def respond(self, messages: Sequence[Message], tools: Sequence[Tool]) -> Message:
        latest = messages[-1]
        if latest["role"] == "tool":
            words = json.loads(latest["content"])["words"]
            return {"role": "assistant", "content": f"Word count: {words}"}
        return {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": "demo-call",
                "type": "function",
                "function": {
                    "name": "count_words",
                    "arguments": json.dumps({"text": latest["content"]}),
                },
            }],
        }


class ChatModel:
    def __init__(self, base_url: str, model: str, api_key: str):
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.model = model
        self.api_key = api_key

    def respond(self, messages: Sequence[Message], tools: Sequence[Tool]) -> Message:
        request = Request(
            self.url,
            data=json.dumps({
                "model": self.model,
                "messages": messages,
                "tools": [tool.definition() for tool in tools],
            }).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                message = json.load(response)["choices"][0]["message"]
            if not isinstance(message, dict):
                raise TypeError("Expected an assistant message object")
            return {
                key: message[key]
                for key in ("role", "content", "tool_calls")
                if key in message and (key != "tool_calls" or message[key])
            }
        except HTTPError as error:
            raise AgentError(f"The model endpoint returned HTTP {error.code}.") from error
        except (URLError, OSError) as error:
            raise AgentError("Could not read the model endpoint.") from error
        except (ValueError, KeyError, IndexError, TypeError) as error:
            raise AgentError("The model endpoint returned an invalid response.") from error
