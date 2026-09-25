"""Classify a user query before routing it to a downstream workflow."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="query_preprocessor",
    title="Query Preprocessor",
    description=(
        "Classify a query, estimate the reasoning effort, and identify the "
        "tools or workflow it needs."
    ),
    fields=(
        FieldSpec(
            name="query",
            label="User query",
            kind="text",
            description="Paste the user's request that should be preprocessed.",
        ),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    """Create a routing plan for one user query."""
    query = request.data.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query_preprocessor requires a non-empty 'query' string")

    state = StateBuilder().add("query", query).build()
    questions = (
        QuestionBuilder()
        .choice(
            name="task_type",
            instructions="What kind of task is the user requesting?",
            criteria={
                "conversation": "Greeting, casual conversation, or general interaction.",
                "question_answering": "Answering a factual or conceptual question.",
                "summarization": "Summarizing or shortening provided content.",
                "extraction": "Extracting structured facts or fields from content.",
                "coding": "Writing, modifying, debugging, or explaining code.",
                "analysis": "Comparing options, interpreting information, or making a recommendation.",
                "other": "The request does not clearly fit another category.",
            },
        )
        .choice(
            name="reasoning_level",
            instructions="How much reasoning effort is needed to answer this query well?",
            criteria={
                "none": "A direct response or simple transformation is sufficient.",
                "low": "Requires a small amount of interpretation or a short sequence of steps.",
                "medium": "Requires multi-step reasoning, comparison, or structured analysis.",
                "high": "Requires deep analysis, planning, difficult tradeoffs, or complex implementation.",
            },
        )
        .choice(
            name="tool_requirement",
            instructions="What tool access does the downstream workflow primarily need?",
            criteria={
                "none": "The query can be answered using the provided prompt and context.",
                "web": "The workflow needs current or externally verified information.",
                "filesystem": "The workflow needs to read or process local files.",
                "code_execution": "The workflow needs to run code or calculate with executable logic.",
                "multiple": "The workflow needs two or more different tool categories.",
            },
        )
        .choice(
            name="route",
            instructions="Which downstream workflow should receive this query first?",
            criteria={
                "general_response": "A normal assistant response is appropriate.",
                "research": "The query should go to a research or web-search workflow.",
                "file_processing": "The query should go to a document or file-processing workflow.",
                "coding_agent": "The query should go to a coding or code-execution workflow.",
                "structured_extraction": "The query should go to a structured extraction workflow.",
                "clarification": "The request is too ambiguous and needs clarification first.",
            },
        )
        .noul(
            name="needs_clarification",
            instructions="Does the user need to provide more information before work can begin?",
            criteria={
                "true": "The request is ambiguous, missing required input, or has conflicting requirements.",
                "false": "The request is sufficiently clear to begin the next workflow.",
            },
        )
        .choice(
            name="risk_level",
            instructions="What is the risk level of acting on this request?",
            criteria={
                "low": "Ordinary low-impact assistance with no meaningful safety concern.",
                "medium": "The response could affect decisions, data, or external systems.",
                "high": "The request involves sensitive, regulated, dangerous, or irreversible action.",
            },
        )
        .build()
    )

    response = inference.infer(state=state, questions=questions)
    return UseCaseResult(
        name="query_preprocessor",
        response=response,
        answers=response.answers,
    )
