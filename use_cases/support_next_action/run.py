"""Choose safe next-step recommendations for a support conversation."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="support_next_action",
    title="Support Next Action",
    description="Recommend the next support step using the conversation and account context.",
    fields=(
        FieldSpec("conversation", "Support conversation", "text", description="The conversation so far."),
        FieldSpec("account_context", "Relevant account context", "text", description="Verified subscription, payment, or account facts."),
        FieldSpec("pending_action", "Pending proposal (optional)", "text", required=False, description="An action the assistant proposed and is awaiting a response to."),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    conversation = request.data.get("conversation")
    context = request.data.get("account_context", "")
    pending = request.data.get("pending_action", "")
    if not isinstance(conversation, str) or not conversation.strip():
        raise ValueError("support_next_action requires a non-empty 'conversation'")
    if not isinstance(context, str) or not isinstance(pending, str):
        raise ValueError("account_context and pending_action must be strings")

    state = StateBuilder().add("conversation", conversation).add("account_context", context).add("pending_action", pending).build()
    questions = (
        QuestionBuilder()
        .choice(
            "customer_intent",
            "What is the customer's primary support intent?",
            {
                "billing": "A charge, refund, invoice, or subscription issue.",
                "technical": "A product bug, error, or setup issue.",
                "account_access": "Login, identity verification, or account access.",
                "cancellation": "The customer wants to cancel or downgrade.",
                "information": "The customer mainly wants an explanation or status.",
                "other": "Another intent or not enough evidence to categorize.",
            },
        )
        .score("urgency", "How urgent is the customer's issue based on the supplied conversation and facts?", ["Routine", "Soon", "Urgent", "Critical"])
        .noul("needs_human_handoff", "Should this conversation be handed to a human agent because of the request, risk, or unresolved issue?")
        .noul("needs_more_information", "Is essential information missing before a safe and useful response can be given?")
        .choice(
            "next_step",
            "What is the safest useful next support step?",
            {
                "answer_with_verified_facts": "Respond using only facts present in the supplied account context.",
                "ask_for_information": "Ask the customer for specific missing information.",
                "investigate_issue": "Continue technical or account investigation.",
                "review_refund_or_billing": "Send the billing or refund request for policy review.",
                "human_handoff": "Transfer the conversation to a human agent.",
            },
        )
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("support_next_action", response, response.answers)
