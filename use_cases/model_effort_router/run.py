"""Choose a model tier and reasoning budget for a bounded task."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="model_effort_router",
    title="Model and Effort Router",
    description="Choose a configured model tier and effort level for a task.",
    fields=(
        FieldSpec("query", "Task", "text", description="The request or task to route."),
        FieldSpec("constraints", "Latency, cost, and quality constraints", "text", description="Describe any applicable constraints."),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    query = request.data.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("model_effort_router requires a non-empty 'query'")
    constraints = request.data.get("constraints", "")
    if not isinstance(constraints, str):
        raise ValueError("'constraints' must be a string")

    state = StateBuilder().add("query", query).add("constraints", constraints).build()
    questions = (
        QuestionBuilder()
        .choice(
            "model_tier",
            "Which configured model tier best fits this task and its constraints?",
            {
                "fast": "Simple, low-risk tasks where speed and cost matter most.",
                "balanced": "Typical tasks needing a balance of quality, speed, and cost.",
                "deep": "Complex, ambiguous, or high-impact tasks needing stronger analysis.",
                "human_review": "The task should be reviewed by a person before a model acts.",
            },
        )
        .choice(
            "reasoning_effort",
            "What reasoning effort should the downstream generative model use?",
            {
                "low": "Direct response or simple transformation.",
                "medium": "Several steps or moderate ambiguity.",
                "high": "Complex planning, extensive analysis, or difficult tradeoffs.",
            },
        )
        .score(
            "task_complexity",
            "Rate the reasoning complexity of the task, independent of its length.",
            ["Very low", "Low", "Moderate", "High", "Very high"],
        )
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("model_effort_router", response, response.answers)
