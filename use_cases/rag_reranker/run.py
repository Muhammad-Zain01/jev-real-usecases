"""Score retrieved passages for relevance to a query."""

import json

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="rag_reranker",
    title="RAG Retrieval Reranker",
    description="Score candidate passages against a query before answer generation.",
    fields=(
        FieldSpec("query", "Search query", "text", description="The information need to answer."),
        FieldSpec(
            "candidates_json",
            "Candidate passages (JSON)",
            "text",
            description='JSON array, e.g. [{"id":"doc_a","text":"..."}]. Include 1–20 candidates.',
        ),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    query = request.data.get("query")
    raw_candidates = request.data.get("candidates_json")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("rag_reranker requires a non-empty 'query'")
    if not isinstance(raw_candidates, str) or not raw_candidates.strip():
        raise ValueError("rag_reranker requires 'candidates_json'")
    try:
        candidates = json.loads(raw_candidates)
    except json.JSONDecodeError as error:
        raise ValueError("'candidates_json' must be valid JSON") from error
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 20:
        raise ValueError("Provide a JSON array containing 1–20 candidate passages")

    ids: set[str] = set()
    normalized = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("Each candidate must be an object with 'id' and 'text'")
        candidate_id, text = candidate.get("id"), candidate.get("text")
        if not isinstance(candidate_id, str) or not candidate_id.strip() or not isinstance(text, str) or not text.strip():
            raise ValueError("Each candidate needs a non-empty string 'id' and 'text'")
        if candidate_id in ids:
            raise ValueError("Candidate ids must be unique")
        ids.add(candidate_id)
        normalized.append({"id": candidate_id, "text": text})

    state = StateBuilder().add("query", query).add("candidates", normalized).build()
    questions = QuestionBuilder()
    for index, candidate in enumerate(normalized):
        questions.score(
            f"relevance_{index}",
            f"How relevant is candidate {candidate['id']} to answering the query? Score semantic usefulness, not keyword overlap alone.",
            ["Irrelevant", "Slightly relevant", "Partly relevant", "Highly relevant", "Directly answers the query"],
        )
    response = inference.infer(state=state, questions=questions.build())
    return UseCaseResult("rag_reranker", response, response.answers)
