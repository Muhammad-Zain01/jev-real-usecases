"""Score a proposed infrastructure change and recommend review depth."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="infrastructure_change_review",
    title="Infrastructure Change Risk Review",
    description="Assess a proposed infrastructure change for operational review; it does not approve or deploy changes.",
    fields=(
        FieldSpec("change", "Proposed change", "text", description="Describe the planned change and affected services."),
        FieldSpec("environment", "Environment and impact", "text", description="Production status, dependencies, users, and blast radius."),
        FieldSpec("validation_rollback", "Validation and rollback", "text", description="Tests, monitoring, rollout plan, and rollback steps."),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    names = ("change", "environment", "validation_rollback")
    values = {name: request.data.get(name) for name in names}
    if any(not isinstance(value, str) or not value.strip() for value in values.values()):
        raise ValueError("infrastructure_change_review requires change, environment, and validation_rollback")
    state = StateBuilder(values).build()
    questions = (
        QuestionBuilder()
        .score("operational_risk", "How much operational risk is indicated by impact, uncertainty, and reversibility?", ["Very low", "Low", "Moderate", "High", "Very high"])
        .noul("rollback_plan_adequate", "Does the supplied plan include a plausible way to detect and reverse a failed change?")
        .choice("review_depth", "What review depth is appropriate?", {
            "standard_review": "The change appears bounded and has adequate validation and rollback details.",
            "peer_review": "A second engineer should review the change and its dependencies.",
            "change_board": "A formal change review should assess the potential impact.",
            "request_more_evidence": "Tests, monitoring, or rollback details are missing.",
            "defer": "The supplied information suggests the change should not proceed yet.",
        })
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("infrastructure_change_review", response, response.answers)
