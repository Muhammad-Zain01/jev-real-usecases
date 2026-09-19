"""The reusable direct-inference client for all Jev use cases."""

from collections.abc import Mapping
from typing import Any

from typesafe_sdk import TypeSafeClient


class JevInference:
    """One reusable Jev client shared by the application and use cases."""

    def __init__(
        self,
        client: TypeSafeClient | None = None,
        model: str = "jev-latest",
    ) -> None:
        self.model = model
        self.client = client or TypeSafeClient(model=model)

    def infer(
        self,
        *,
        state: Any,
        questions: Mapping[str, Any],
    ) -> Any:
        """Send one direct System One request to Jev."""

        # This is the actual Jev API call.
        return self.client.system_one(
            state=state,
            questions=questions,
            model=self.model,
        )

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "JevInference":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
