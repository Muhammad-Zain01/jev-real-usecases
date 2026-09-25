"""Detect language and recommend a locale-aware handling path."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="language_locale_router",
    title="Language and Locale Router",
    description="Identify the language of a message and route it to an appropriate queue.",
    fields=(FieldSpec("message", "Message", "text", description="Paste the user's message, preserving its original language."),),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    message = request.data.get("message")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("language_locale_router requires non-empty 'message'")
    state = StateBuilder().add("message", message).build()
    questions = (
        QuestionBuilder()
        .choice("language", "What language is primarily used in the message?", {
            "english": "Primarily English.",
            "spanish": "Primarily Spanish.",
            "french": "Primarily French.",
            "arabic": "Primarily Arabic.",
            "urdu": "Primarily Urdu.",
            "other_language": "A language not listed above.",
            "unclear": "Too little or too mixed text to identify reliably.",
        })
        .noul("mixed_language", "Does the message meaningfully mix two or more languages?")
        .choice("handling", "What language handling should be used?", {
            "same_language_queue": "Use a support queue that can handle the detected language.",
            "translation_then_support": "Translate for support review while preserving the original message.",
            "request_clarification": "Ask which language the user prefers.",
            "manual_review": "A person should identify the language or appropriate route.",
        })
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("language_locale_router", response, response.answers)
