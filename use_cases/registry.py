"""Available use cases for the UI."""

from importlib import import_module


def _load(module_path: str):
    """Load one same-named use-case file from its folder."""
    return import_module(module_path)


support_routing = _load("use_cases.support_routing.run")
resume_parsing = _load("use_cases.resume_parsing.run")
query_preprocessor = _load("use_cases.query_preprocessor.run")
agent_router = _load("use_cases.agent_router.run")
tool_policy_gate = _load("use_cases.tool_policy_gate.run")
model_effort_router = _load("use_cases.model_effort_router.run")
rag_reranker = _load("use_cases.rag_reranker.run")
agent_trace_reviewer = _load("use_cases.agent_trace_reviewer.run")
prompt_safety_gate = _load("use_cases.prompt_safety_gate.run")
support_next_action = _load("use_cases.support_next_action.run")
invoice_triage = _load("use_cases.invoice_triage.run")
security_incident_triage = _load("use_cases.security_incident_triage.run")
email_triage = _load("use_cases.email_triage.run")
product_feedback_triage = _load("use_cases.product_feedback_triage.run")
operations_event_router = _load("use_cases.operations_event_router.run")
document_intake_router = _load("use_cases.document_intake_router.run")
workflow_failure_triage = _load("use_cases.workflow_failure_triage.run")
language_locale_router = _load("use_cases.language_locale_router.run")
sla_breach_prioritizer = _load("use_cases.sla_breach_prioritizer.run")
complaint_escalation = _load("use_cases.complaint_escalation.run")
infrastructure_change_review = _load("use_cases.infrastructure_change_review.run")
data_quality_triage = _load("use_cases.data_quality_triage.run")
duplicate_case_review = _load("use_cases.duplicate_case_review.run")
reviewer_queue_assignment = _load("use_cases.reviewer_queue_assignment.run")


USE_CASES = {
    support_routing.SPEC.id: support_routing,
    resume_parsing.SPEC.id: resume_parsing,
    query_preprocessor.SPEC.id: query_preprocessor,
    agent_router.SPEC.id: agent_router,
    tool_policy_gate.SPEC.id: tool_policy_gate,
    model_effort_router.SPEC.id: model_effort_router,
    rag_reranker.SPEC.id: rag_reranker,
    agent_trace_reviewer.SPEC.id: agent_trace_reviewer,
    prompt_safety_gate.SPEC.id: prompt_safety_gate,
    support_next_action.SPEC.id: support_next_action,
    invoice_triage.SPEC.id: invoice_triage,
    security_incident_triage.SPEC.id: security_incident_triage,
    email_triage.SPEC.id: email_triage,
    product_feedback_triage.SPEC.id: product_feedback_triage,
    operations_event_router.SPEC.id: operations_event_router,
    document_intake_router.SPEC.id: document_intake_router,
    workflow_failure_triage.SPEC.id: workflow_failure_triage,
    language_locale_router.SPEC.id: language_locale_router,
    sla_breach_prioritizer.SPEC.id: sla_breach_prioritizer,
    complaint_escalation.SPEC.id: complaint_escalation,
    infrastructure_change_review.SPEC.id: infrastructure_change_review,
    data_quality_triage.SPEC.id: data_quality_triage,
    duplicate_case_review.SPEC.id: duplicate_case_review,
    reviewer_queue_assignment.SPEC.id: reviewer_queue_assignment,
}


def get_use_case(use_case_id: str):
    """Return a registered use-case module by its stable id."""
    try:
        return USE_CASES[use_case_id]
    except KeyError as error:
        raise ValueError(f"Unknown use case: {use_case_id}") from error
