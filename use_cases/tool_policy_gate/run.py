"""Classify a proposed tool operation against supplied policy context."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="tool_policy_gate",
    title="Tool Selection and Policy Gate",
    description="Assess a proposed tool operation before application code considers it.",
    fields=(
        FieldSpec("request", "User request", "text", description="What the user asked for."),
        FieldSpec("proposed_action", "Proposed tool action", "text", description="Describe the intended operation and target."),
        FieldSpec("available_tools", "Available tools and policy", "text", description="List tools, permissions, and approval rules."),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    values = {name: request.data.get(name) for name in ("request", "proposed_action", "available_tools")}
    if any(not isinstance(value, str) or not value.strip() for value in values.values()):
        raise ValueError("tool_policy_gate requires request, proposed_action, and available_tools")

    state = StateBuilder(values).build()
    questions = (
        QuestionBuilder()
        .choice(
            "tool_category",
            "Which tool category best matches the proposed action?",
            {
                "web": "Search or retrieve public online information.",
                "filesystem": "Read or modify local files.",
                "code_execution": "Run code or calculations in an execution environment.",
                "communication": "Send messages or contact people or services.",
                "data_system": "Read or change a database or business system.",
                "none": "No tool is needed or the action does not fit a category.",
            },
        )
        .noul(
            "policy_allows_action",
            "Based only on the supplied policy and context, is this action permitted?",
        )
        .noul(
            "requires_human_approval",
            "Does this action require human approval before execution under the supplied policy or because of its impact?",
        )
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("tool_policy_gate", response, response.answers)
