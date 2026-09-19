"""Available use cases for the UI."""

from importlib import import_module


def _load(module_path: str):
    """Load one same-named use-case file from its folder."""
    return import_module(module_path)


support_routing = _load("use_cases.support_routing.run")
resume_parsing = _load("use_cases.resume_parsing.run")


USE_CASES = {
    support_routing.SPEC.id: support_routing,
    resume_parsing.SPEC.id: resume_parsing,
}


def get_use_case(use_case_id: str):
    """Return a registered use-case module by its stable id."""
    try:
        return USE_CASES[use_case_id]
    except KeyError as error:
        raise ValueError(f"Unknown use case: {use_case_id}") from error
