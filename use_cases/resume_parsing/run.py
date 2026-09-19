"""Resume parsing use case."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="resume_parsing",
    title="Resume Parsing",
    description="Review a resume and return structured candidate attributes.",
    fields=(
        FieldSpec(
            name="resume_file",
            label="Resume file",
            kind="file",
            description="Upload a TXT, PDF, or DOCX resume.",
        ),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    """Evaluate structured attributes of one normalized resume."""
    resume_text = request.data.get("resume_text")
    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("resume_parsing requires non-empty 'resume_text'")

    state = StateBuilder().add("resume_text", resume_text).build()
    questions = (
        QuestionBuilder()
        .choice(
            name="seniority",
            instructions="What is the candidate's seniority level?",
            criteria={
                "intern": "Little or no professional experience.",
                "junior": "Early-career professional.",
                "mid": "Independent professional with meaningful experience.",
                "senior": "Experienced professional who can lead complex work.",
                "lead": "Leadership, ownership, or management responsibilities.",
            },
        )
        .choice(
            name="primary_role",
            instructions="What is the candidate's primary professional area?",
            criteria={
                "software_engineering": "Builds software or engineering systems.",
                "data": "Works primarily with data, analytics, or machine learning.",
                "product": "Works primarily in product management or strategy.",
                "design": "Works primarily in UX, UI, or visual design.",
                "other": "None of the categories clearly applies.",
            },
        )
        .noul(
            name="has_python_experience",
            instructions="Does the resume show Python experience?",
        )
        .score(
            name="software_engineering_match",
            instructions="How strong is the match for a software engineering role?",
            criteria=[
                "No meaningful match",
                "Weak match",
                "Moderate match",
                "Strong match",
                "Excellent match",
            ],
        )
        .build()
    )

    response = inference.infer(state=state, questions=questions)
    return UseCaseResult(
        name="resume_parsing",
        response=response,
        answers=response.answers,
    )
