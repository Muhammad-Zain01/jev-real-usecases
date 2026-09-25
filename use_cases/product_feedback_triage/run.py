"""Classify product feedback and estimate its impact."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="product_feedback_triage",
    title="Product Feedback Triage",
    description="Classify customer feedback and recommend where it should go.",
    fields=(FieldSpec("feedback", "Customer feedback", "text", description="Paste the feedback and any relevant product context."),),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    feedback = request.data.get("feedback")
    if not isinstance(feedback, str) or not feedback.strip():
        raise ValueError("product_feedback_triage requires non-empty 'feedback'")
    state = StateBuilder().add("feedback", feedback).build()
    questions = (
        QuestionBuilder()
        .choice("feedback_type", "What kind of feedback is this?", {
            "bug_report": "Reports a defect, failure, or unexpected behavior.",
            "feature_request": "Requests a new capability or change.",
            "usability_issue": "Describes confusion, friction, or difficulty using the product.",
            "praise": "Positive feedback without a concrete issue or request.",
            "other": "Feedback does not fit another category.",
        })
        .score("user_impact", "How much user impact is described?", ["Minimal", "Low", "Moderate", "High", "Severe"])
        .choice("destination", "Where should this feedback be routed?", {
            "engineering": "A reproducible defect needs technical investigation.",
            "product": "A feature or product decision needs evaluation.",
            "design_research": "A usability problem needs user-experience investigation.",
            "customer_success": "A customer-facing follow-up is appropriate.",
            "feedback_archive": "Keep as feedback without immediate follow-up.",
        })
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("product_feedback_triage", response, response.answers)
