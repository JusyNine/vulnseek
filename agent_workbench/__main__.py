import argparse
import os

from .models import ChatModel, DemoModel
from .runtime import AgentError, run
from .tools import WORD_COUNT


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a tool-using agent.")
    parser.add_argument("prompt")
    parser.add_argument("--demo", action="store_true", help="Count words offline.")
    args = parser.parse_args()
    if args.demo:
        model = DemoModel()
    else:
        base_url = os.getenv("AGENT_BASE_URL")
        model_name = os.getenv("AGENT_MODEL")
        api_key = os.getenv("AGENT_API_KEY")
        if not all((base_url, model_name, api_key)):
            parser.error("Set AGENT_BASE_URL, AGENT_MODEL, and AGENT_API_KEY, or use --demo.")
        model = ChatModel(base_url, model_name, api_key)
    try:
        print(run(args.prompt, model, {WORD_COUNT.name: WORD_COUNT}))
    except AgentError as error:
        parser.exit(1, f"Agent error: {error}\n")


if __name__ == "__main__":
    main()
