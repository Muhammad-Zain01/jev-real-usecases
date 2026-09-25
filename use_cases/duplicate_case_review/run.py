"""Compare a new case with candidate cases for duplicate or related records."""

import json

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="duplicate_case_review",
    title="Duplicate Case Review",
    description="Compare a case with likely matches and recommend whether it is duplicate or related.",
    fields=(
        FieldSpec("new_case", "New case", "text", description="The case being reviewed."),
        FieldSpec("candidates_json", "Candidate cases (JSON)", "text", description='JSON array, e.g. [{"id":"CASE-123","summary":"..."}]. Include 1–20 candidates.'),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    new_case = request.data.get("new_case")
    raw_candidates = request.data.get("candidates_json")
    if not isinstance(new_case, str) or not new_case.strip():
        raise ValueError("duplicate_case_review requires a non-empty 'new_case'")
    if not isinstance(raw_candidates, str) or not raw_candidates.strip():
        raise ValueError("duplicate_case_review requires 'candidates_json'")
    try:
        candidates = json.loads(raw_candidates)
    except json.JSONDecodeError as error:
        raise ValueError("'candidates_json' must be valid JSON") from error
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 20:
        raise ValueError("Provide a JSON array containing 1–20 candidate cases")

    ids: set[str] = set()
    normalized = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("Each candidate must be an object with 'id' and 'summary'")
        candidate_id, summary = candidate.get("id"), candidate.get("summary")
        if not isinstance(candidate_id, str) or not candidate_id.strip() or not isinstance(summary, str) or not summary.strip():
            raise ValueError("Each candidate needs a non-empty string 'id' and 'summary'")
        if candidate_id in ids:
            raise ValueError("Candidate ids must be unique")
        ids.add(candidate_id)
        normalized.append({"id": candidate_id, "summary": summary})

    state = StateBuilder().add("new_case", new_case).add("candidate_cases", normalized).build()
    questions = QuestionBuilder().choice("relationship", "How does the new case relate to the candidate cases overall?", {
        "duplicate": "At least one candidate appears to describe the same underlying issue or request.",
        "related": "A candidate concerns the same broader topic but is a distinct issue or request.",
        "separate": "The candidates appear to describe separate issues.",
        "uncertain": "The supplied summaries do not support a reliable comparison.",
    })
    for index, candidate in enumerate(normalized):
        questions.noul(
            f"duplicate_{index}",
            f"Does candidate {candidate['id']} describe the same underlying issue or request as the new case?",
        )
    response = inference.infer(state=state, questions=questions.build())
    return UseCaseResult("duplicate_case_review", response, response.answers)
