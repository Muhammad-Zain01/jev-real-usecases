"""Classify a data quality issue and recommend its owner or response."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="data_quality_triage",
    title="Data Quality Issue Triage",
    description="Classify a reported data issue and route it for investigation.",
    fields=(
        FieldSpec("issue", "Data issue", "text", description="Describe the affected data and observed problem."),
        FieldSpec("expected_actual", "Expected versus observed", "text", description="Include examples, timestamps, and the expected behavior."),
        FieldSpec("pipeline_context", "Dataset and pipeline context", "text", description="Dataset owner, source, downstream consumers, and recent pipeline changes."),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    names = ("issue", "expected_actual", "pipeline_context")
    values = {name: request.data.get(name) for name in names}
    if any(not isinstance(value, str) or not value.strip() for value in values.values()):
        raise ValueError("data_quality_triage requires issue, expected_actual, and pipeline_context")
    state = StateBuilder(values).build()
    questions = (
        QuestionBuilder()
        .choice("issue_type", "What kind of data quality issue is described?", {
            "missing_data": "Expected records or fields are absent.",
            "stale_data": "Data is delayed or not updated as expected.",
            "inconsistent_data": "Values disagree across records, sources, or systems.",
            "malformed_data": "Values have an invalid format or violate a schema expectation.",
            "unexpected_distribution": "Values or counts appear unusual compared with expected behavior.",
            "unclear": "The supplied evidence does not identify the issue type.",
        })
        .score("downstream_impact", "How significant is the potential downstream impact?", ["Minimal", "Low", "Moderate", "High", "Critical"])
        .choice("owner_route", "Which team should investigate first?", {
            "source_system_owner": "The originating application or source system likely owns the issue.",
            "data_pipeline_owner": "Ingestion or transformation logic likely owns the issue.",
            "analytics_consumer": "A downstream report or consumer definition may be responsible.",
            "data_governance": "A shared definition, quality standard, or access policy needs review.",
            "manual_triage": "A person should identify the owner.",
        })
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("data_quality_triage", response, response.answers)
