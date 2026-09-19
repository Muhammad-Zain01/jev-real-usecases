"""A small next-token generation experiment powered by Jev.

Run from the repository root with:

    python -m experiments.simulate_llm
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

load_dotenv()

# Allow this experiment to be run directly with `python3 experiments/simulate_llm.py`.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from inference import JevInference, QuestionBuilder, StateBuilder


DEFAULT_VOCABULARY = (
    " Hello",
    " Hi",
    " Hey",
    " Welcome",
    " Good",
    " morning",
    " afternoon",
    " evening",
    " there",
    " feeling",
    " nice",
    " to",
    " meet",
    " you",
    "!",
    " How",
    " are",
    " things",
    " going",
    " doing",
    " today",
    "?",
    " I",
    " am",
    " here",
    " help",
    " with",
    " your",
    " question",
    " What",
    " would",
    " like",
    " know",
    " Let",
    " me",
    " Thanks",
    " for",
    " asking",
    " reaching",
    " out",
    " Could",
    " you",
    " tell",
    " me",
    " more",
    " about",
    " that",
    " Please",
    " sure",
    " absolutely",
    " great",
    " sounds",
    " good",
    " let's",
    " get",
    " started",
    ".",
    "[END]",
)


def select_top_token(probabilities: dict[str, float]) -> str:
    """Select the token with the highest probability."""
    return max(probabilities, key=probabilities.get)


def parse_bool(value: str) -> bool:
    """Parse common command-line boolean spellings."""
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y", "on"}:
        return True
    if normalized in {"false", "0", "no", "n", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def generate(
    inference: JevInference,
    prompt: str,
    vocabulary: tuple[str, ...] = DEFAULT_VOCABULARY,
    max_steps: int = 20,
    verbose: bool = True,
) -> dict[str, Any]:
    """Generate an assistant reply by repeatedly choosing one vocabulary item."""
    reply = ""
    tokens: list[str] = []
    trace: list[dict[str, Any]] = []

    print(f"user: {prompt}")
    print("assistant: ", end="", flush=True)

    for step in range(max_steps):
        state = (
            StateBuilder()
            .add(
                "conversation",
                [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": reply},
                ],
            )
            .add("task", "Generate exactly one next token for the assistant reply.")
            .add("step", step)
            .build()
        )

        questions = (
            QuestionBuilder()
            .choice(
                name="next_token",
                instructions=(
                    "Which candidate token should come next in the assistant's reply?"
                ),
                criteria={
                    token: (
                        "Stop the assistant reply because the message is complete."
                        if token == "[END]"
                        else f"Append this candidate token to the assistant reply: {token!r}"
                    )
                    for token in vocabulary
                },
            )
            .build()
        )

        if verbose:
            separator = "=" * 78
            print(
                f"\n\n{separator}\n"
                f"STEP {step + 1:02d} · REQUEST TO JEV\n"
                f"{separator}\n"
                f"{json.dumps(state, ensure_ascii=False, indent=2)}",
                file=sys.stderr,
            )

        response = inference.infer(state=state, questions=questions)
        answer = response.choices["next_token"]
        # Greedy decoding: always choose Jev's highest-probability token.
        token = select_top_token(answer.probabilities)

        if verbose:
            print(
                f"\n{separator}\n"
                f"STEP {step + 1:02d} · JEV RESPONSE\n"
                f"{separator}\n"
                f"model: {response.model}\n"
                f"top choice: {answer.choice!r}\n"
                f"confidence: {answer.confidence:.3f}\n"
                "selection: greedy highest probability\n"
                "probabilities (highest first):",
                file=sys.stderr,
            )
            for candidate, probability in sorted(
                answer.probabilities.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:10]:
                print(f"  {candidate!r}: {probability:.3f}", file=sys.stderr)
            print(f"sampled token: {token!r}", file=sys.stderr)

        trace.append(
            {
                "step": step,
                "selected_token": token,
                "confidence": answer.confidence,
                "probabilities": answer.probabilities,
            }
        )

        if token == "[END]":
            break

        tokens.append(token)
        reply += token
        print(token, end="", flush=True)

    print()

    return {
        "text": reply,
        "tokens": tokens,
        "trace": trace,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate text with a tiny Jev vocabulary.")
    parser.add_argument(
        "--prompt",
        default=None,
        help="User message that starts the conversation.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=20,
        help="Maximum number of Jev calls.",
    )
    parser.add_argument(
        "--debug",
        nargs="?",
        const=True,
        default=False,
        type=parse_bool,
        help="Show Jev request/response logs. Use --debug=true; default is false.",
    )
    args = parser.parse_args()

    if not os.getenv("TYPESAFE_API_KEY"):
        raise SystemExit(
            "TYPESAFE_API_KEY is not loaded. Run 'set -a; source .env; set +a' first."
        )

    with JevInference() as inference:
        pending_prompt = args.prompt

        while True:
            if pending_prompt is None:
                try:
                    pending_prompt = input("\n> ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nExiting.")
                    break

            if pending_prompt.lower() in {"exit", "quit", ":q"}:
                print("Exiting.")
                break

            if not pending_prompt:
                pending_prompt = None
                continue

            result = generate(
                inference=inference,
                prompt=pending_prompt,
                max_steps=args.max_steps,
                verbose=args.debug,
            )

            if args.debug:
                print(
                    f"debug summary: {len(result['tokens'])} tokens generated",
                    file=sys.stderr,
                )

            pending_prompt = None


if __name__ == "__main__":
    main()
