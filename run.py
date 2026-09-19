"""Run the first real-world Jev use case."""

import os

from inference import JevInference
from use_cases import UseCaseInput
from use_cases.registry import get_use_case


def main() -> None:
    if not os.getenv("TYPESAFE_API_KEY"):
        raise SystemExit(
            "TYPESAFE_API_KEY is not loaded. Run 'set -a; source .env; set +a' first."
        )

    ticket = "I was charged twice for my subscription and need one charge refunded."

    with JevInference() as inference:
        result = get_use_case("support_routing").run(
            inference,
            UseCaseInput(data={"ticket": ticket}),
        )

    answer = result.answers["category"]
    print(f"use case: {result.name}")
    print(f"model: {result.response.model}")
    print(f"ticket: {ticket}")
    print(f"category: {answer.choice}")
    print(f"confidence: {answer.confidence}")
    print(f"probabilities: {answer.probabilities}")


if __name__ == "__main__":
    main()
