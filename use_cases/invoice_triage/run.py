"""Recommend an invoice review outcome from supplied business records."""

from inference import JevInference, QuestionBuilder, StateBuilder

from ..contract import FieldSpec, UseCaseInput, UseCaseResult, UseCaseSpec


SPEC = UseCaseSpec(
    id="invoice_triage",
    title="Invoice Processing Triage",
    description="Compare invoice context and recommend a review outcome; this does not initiate payment.",
    fields=(
        FieldSpec("invoice", "Invoice details", "text", description="Invoice number, vendor, line items, totals, tax, and payment details."),
        FieldSpec("purchase_order", "Purchase order or contract", "text", description="Ordered items, rates, quantities, and payment terms."),
        FieldSpec("vendor_record", "Vendor record", "text", description="Verified vendor identity and payment details on file."),
        FieldSpec("delivery_evidence", "Delivery and approval evidence", "text", description="Receiving notes, service evidence, and approvals."),
        FieldSpec("prior_invoices", "Prior invoices (optional)", "text", required=False, description="Relevant prior invoices or payment records."),
    ),
)


def run(inference: JevInference, request: UseCaseInput) -> UseCaseResult:
    names = ("invoice", "purchase_order", "vendor_record", "delivery_evidence")
    values = {name: request.data.get(name) for name in names}
    if any(not isinstance(value, str) or not value.strip() for value in values.values()):
        raise ValueError("invoice_triage requires invoice, purchase_order, vendor_record, and delivery_evidence")
    prior = request.data.get("prior_invoices", "")
    if not isinstance(prior, str):
        raise ValueError("'prior_invoices' must be a string")
    values["prior_invoices"] = prior

    state = StateBuilder(values).build()
    questions = (
        QuestionBuilder()
        .noul("is_invoice", "Does the supplied document appear to be an invoice for the stated vendor?")
        .noul("possible_duplicate", "Do the supplied records indicate this invoice may already have been submitted or paid?")
        .noul("vendor_mismatch", "Is there a meaningful mismatch between invoice vendor/payment details and the verified vendor record?")
        .choice(
            "discrepancy_type",
            "What is the most important discrepancy, if any?",
            {
                "none_apparent": "No material discrepancy is apparent from the supplied records.",
                "amount_or_quantity": "Totals, rates, or quantities do not align.",
                "delivery_or_approval": "Delivery evidence or required approval is missing or inconsistent.",
                "vendor_or_payment": "Vendor identity or payment details conflict.",
                "document_quality": "The invoice is incomplete, unclear, or needs correction.",
            },
        )
        .choice(
            "recommended_next_step",
            "What is the appropriate review recommendation?",
            {
                "route_for_approval": "The records appear consistent but require the normal approval process.",
                "hold_for_documents": "Pause review until missing evidence or documents are provided.",
                "request_correction": "Ask the vendor or submitter to correct the invoice.",
                "dispute_line_items": "Review or dispute specific line items before any payment decision.",
                "fraud_or_duplicate_review": "Send for specialist fraud or duplicate-payment review.",
                "human_review": "A person should reconcile the records before any decision.",
            },
        )
        .build()
    )
    response = inference.infer(state=state, questions=questions)
    return UseCaseResult("invoice_triage", response, response.answers)
