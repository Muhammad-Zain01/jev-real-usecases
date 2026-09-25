"""Recommend a review queue and priority for a case."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="reviewer_queue_assignment",
    title="Human Review Queue Assignment",
    description="Match a case to a review queue and estimate its priority.",
    fields=(
        FieldSpec("case", "Case summary", "text", description="Describe the issue and the decision needed."),
        FieldSpec("queue_capabilities", "Queue capabilities", "text", description="List the review queues, their expertise, and any stated constraints."),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    case, queues = request.data.get("case"), request.data.get("queue_capabilities")
    if not isinstance(case, str) or not case.strip() or not isinstance(queues, str) or not queues.strip():
        raise ValueError("reviewer_queue_assignment requires case and queue_capabilities")
    state = StateBuilder().add("case", case).add("queue_capabilities", queues).build()
    questions = (
        QuestionBuilder()
        .choice("expertise", "What expertise is most relevant to reviewing this case?", {
            "technical": "Software, infrastructure, or system expertise.",
            "billing_finance": "Payments, accounting, or financial operations.",
            "security_privacy": "Security, privacy, or access control.",
            "customer_operations": "Customer support, service, or account operations.",
            "legal_compliance": "Legal, regulatory, or policy interpretation.",
            "general": "No specialist expertise is clearly required.",
        })
        .score("review_priority", "How quickly should this case be reviewed given its impact and stated constraints?", ["Routine", "Normal", "High", "Urgent"])
        .choice("queue", "Which queue from the supplied queue capabilities best fits this case?", {
            "technical": "The listed technical or engineering review queue.",
            "finance": "The listed billing or finance review queue.",
            "security": "The listed security or privacy review queue.",
            "customer_operations": "The listed customer operations queue.",
            "legal_compliance": "The listed legal or compliance review queue.",
            "general": "The listed general review queue.",
            "manual_assignment": "No suitable queue is clear; a person should assign it.",
        })
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("reviewer_queue_assignment", response, response.answers)
