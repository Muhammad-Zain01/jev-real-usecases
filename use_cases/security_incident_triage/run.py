"""Triage a security alert and recommend a human-reviewed response."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="security_incident_triage",
    title="Security Incident Triage",
    description="Assess an alert and recommend a response path; no containment action is executed.",
    fields=(
        FieldSpec("alert", "Security alert", "text", description="Alert details, evidence, and event time."),
        FieldSpec("asset_context", "Asset and identity context", "text", description="Asset owner, environment, tier, and relevant identity facts."),
        FieldSpec("related_activity", "Related tickets or maintenance", "text", description="Open incidents, approved changes, or scheduled maintenance."),
        FieldSpec("authorizations", "Standing authorizations", "text", description="Verified permissions relevant to this event."),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    names = ("alert", "asset_context", "related_activity", "authorizations")
    values = {name: request.data.get(name) for name in names}
    if any(not isinstance(value, str) or not value.strip() for value in values.values()):
        raise ValueError("security_incident_triage requires alert, asset_context, related_activity, and authorizations")

    state = StateBuilder(values).build()
    questions = (
        QuestionBuilder()
        .noul("likely_unauthorized", "Does the supplied evidence suggest the observed activity was unauthorized?")
        .noul("explained_by_known_change", "Do the supplied records provide a credible authorized explanation for the alert?")
        .score("evidence_strength", "How strong is the evidence supporting a security incident?", ["Very weak", "Weak", "Mixed", "Strong", "Very strong"])
        .choice(
            "recommended_response",
            "What response path should be recommended for analyst review?",
            {
                "close_with_reason": "Records adequately explain the alert and no material concern remains.",
                "queue_for_analysis": "The alert needs routine analyst investigation.",
                "escalate_urgently": "Evidence or asset impact justifies urgent incident response review.",
                "containment_review": "Consider containment, but require an authorized responder to approve and execute it.",
            },
        )
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("security_incident_triage", response, response.answers)
