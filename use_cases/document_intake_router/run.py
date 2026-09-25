"""Identify a document type and recommend its processing workflow."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="document_intake_router",
    title="Document Intake Router",
    description="Classify supplied document text and select a downstream parser or review path.",
    fields=(FieldSpec("document_text", "Document text", "text", description="Paste extracted text or a short document preview."),),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    document = request.data.get("document_text")
    if not isinstance(document, str) or not document.strip():
        raise ValueError("document_intake_router requires non-empty 'document_text'")
    state = StateBuilder().add("document_text", document).build()
    questions = (
        QuestionBuilder()
        .choice("document_type", "What kind of document is this?", {
            "invoice": "A request for payment for goods or services.",
            "receipt": "Evidence of a completed purchase or payment.",
            "purchase_order": "An order authorizing purchase of goods or services.",
            "resume": "A candidate's employment or education history.",
            "contract": "An agreement describing obligations or terms.",
            "other": "Another document type or insufficient evidence.",
        })
        .score("classification_confidence", "How clear is the evidence for the selected document type?", ["Unclear", "Weak", "Moderate", "Strong", "Very strong"])
        .choice("processing_route", "Which downstream handling path fits?", {
            "invoice_review": "Extract and reconcile invoice fields.",
            "receipt_extraction": "Extract merchant, date, and line-item evidence.",
            "order_matching": "Compare an order with related invoices or receipts.",
            "resume_parsing": "Extract candidate attributes from a resume.",
            "contract_review": "Send agreement text for clause or obligation review.",
            "human_review": "A person should identify or handle this document.",
        })
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("document_intake_router", response, response.answers)
