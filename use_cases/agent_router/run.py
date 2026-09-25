"""Choose a registered specialist workflow for an incoming request."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="agent_router",
    title="Agent Router",
    description="Select an available specialist workflow for a user request.",
    fields=(
        FieldSpec("query", "User request", "text", description="The request to route."),
        FieldSpec(
            "available_agents",
            "Available agents",
            "text",
            description="List each available agent and its capabilities.",
        ),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    """Return a route label; the caller remains responsible for dispatch."""
    query = request.data.get("query")
    agents = request.data.get("available_agents")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("agent_router requires a non-empty 'query'")
    if not isinstance(agents, str) or not agents.strip():
        raise ValueError("agent_router requires non-empty 'available_agents'")

    state = StateBuilder().add("query", query).add("available_agents", agents).build()
    questions = (
        QuestionBuilder()
        .choice(
            "route",
            "Which available specialist best fits this request? Select clarify if required information is missing, or no_match if none fits.",
            {
                "research_agent": "Finds and synthesizes external or supplied information.",
                "coding_agent": "Writes, reviews, or debugs software.",
                "document_agent": "Reads, extracts, or transforms uploaded documents.",
                "support_agent": "Handles customer or internal support workflows.",
                "general_agent": "Handles requests that do not need a specialist.",
                "clarify": "The request needs clarification before routing.",
                "no_match": "No listed agent is suitable for the request.",
            },
        )
        .score(
            "route_fit",
            "How well does the selected route fit the request and the listed agent capabilities?",
            ["Poor", "Weak", "Adequate", "Strong", "Excellent"],
        )
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("agent_router", response, response.answers)
