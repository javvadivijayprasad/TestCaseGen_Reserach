"""Five-element prompt-engineering taxonomy for RAITG.

The taxonomy:
  1. Role specification
  2. Context injection
  3. Task directive
  4. Heuristic scaffold
  5. Output contract
"""

from __future__ import annotations

import json
from typing import Any

PROMPT_VERSION = "raitg-prompt-v1.0.0"


# ---------------------------------------------------------------------------
# Element 1: role specification
# ---------------------------------------------------------------------------
ROLE_SENIOR_QA = (
    "You are a senior software quality engineer with 12+ years of experience "
    "designing test suites for production systems. You are fluent in BDD, "
    "Gherkin, pytest, Playwright, and REST API testing. You write tests that "
    "are precise, deterministic, and traceable to source requirements. You "
    "follow ISO/IEC/IEEE 29119-4 test design techniques."
)


# ---------------------------------------------------------------------------
# Element 2: context injection
# ---------------------------------------------------------------------------
def context_block(req: dict[str, Any], glossary: dict[str, str] | None = None,
                  exemplars: list[dict[str, Any]] | None = None) -> str:
    parts = ["[CONTEXT]"]
    parts.append(f"Requirement ID: {req['id']}")
    parts.append(f"Domain: {req['domain']}")
    parts.append(f"Layer: {req['layer']}")
    parts.append(f"Category: {req['category']}")
    parts.append(f"Title: {req['title']}")
    parts.append(f"Statement: {req['statement']}")
    parts.append(f"Actors: {', '.join(req.get('actors') or [])}")
    parts.append(f"Preconditions: {'; '.join(req.get('preconditions') or [])}")
    parts.append(f"Triggers: {'; '.join(req.get('triggers') or [])}")
    parts.append(f"Expected outcomes: {'; '.join(req.get('expected_outcomes') or [])}")
    parts.append(f"Error pathways: {'; '.join(req.get('error_pathways') or [])}")
    parts.append(f"Target app: {req.get('target_app')}")
    parts.append(f"Endpoint/screen: {req.get('target_endpoint_or_screen')}")
    if glossary:
        parts.append(f"Glossary: {json.dumps(glossary)}")
    if exemplars:
        parts.append("Exemplars (for style only, do not copy):")
        for ex in exemplars[:3]:
            parts.append("---")
            parts.append(json.dumps(ex, indent=2))
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Element 3: task directive
# ---------------------------------------------------------------------------
FRAMEWORK_HINTS = {
    "pytest": (
        "Emit Python test functions named test_* that can run under `pytest`. "
        "Prefer `requests` or simple `httpx` for API assertions; avoid heavy fixtures."
    ),
    "playwright-ts": (
        "Emit TypeScript tests using `@playwright/test`. Use `test()`, `expect()`, "
        "page.getByRole / getByTestId. Avoid arbitrary sleeps; use expect() with auto-wait."
    ),
    "selenium-java": (
        "Emit a Java JUnit5 test class using Selenium WebDriver 4+. Use @Test, "
        "Assertions, WebDriverWait with ExpectedConditions. No Thread.sleep."
    ),
    "selenium-python": (
        "Emit pytest tests using selenium.webdriver. Use WebDriverWait + expected_conditions. "
        "Prefer explicit waits over sleep."
    ),
    "selenium-ts": (
        "Emit TypeScript/Mocha tests using selenium-webdriver. Use until.elementLocated."
    ),
    "cypress-ts": (
        "Emit Cypress TypeScript specs using `describe/it`, `cy.visit()`, `cy.get()`, "
        "`cy.contains()`, and `cy.request()`. Use `.should()` for assertions."
    ),
    "gherkin": (
        "Emit a Gherkin .feature file with Given/When/Then steps. One Feature, multiple Scenarios."
    ),
    "postman": (
        "Emit a Postman v2.1 collection JSON with Pre-request and Test scripts "
        "using pm.test() and pm.expect()."
    ),
}


def task_directive(target_framework: str) -> str:
    hint = FRAMEWORK_HINTS.get(target_framework, "")
    hint_block = f"\n\nFRAMEWORK NOTES:\n  {hint}" if hint else ""
    return (
        "[TASK]\n"
        "Generate a test suite for the requirement above. The suite must include "
        "AT LEAST one positive case, one negative case, and one boundary case. "
        f"The target framework is {target_framework}. "
        "Each test case must be self-contained, deterministic, and idempotent.\n\n"
        "IMPORTANT LIMITS:\n"
        "  - Keep each `executable` field to AT MOST 40 lines of code.\n"
        "  - Use placeholders (e.g. <helper_fn>, <fixture>) rather than full helper code.\n"
        "  - Do NOT include license headers, long import lists, or multi-line docstrings.\n"
        "  - Always properly escape internal double-quotes in JSON string values.\n"
        "  - Prefer concise assertions over comprehensive setup/teardown."
        + hint_block
    )


# ---------------------------------------------------------------------------
# Element 4: heuristic scaffold
# ---------------------------------------------------------------------------
HEURISTIC_SCAFFOLD = (
    "[HEURISTICS]\n"
    "Apply the following classical test design heuristics; cite which heuristic each "
    "test embodies in the `heuristic` field:\n"
    "  - Equivalence Partitioning (EP)\n"
    "  - Boundary Value Analysis (BVA)\n"
    "  - State Transition Coverage (STC)\n"
    "  - Decision Table (DT)\n"
    "  - Negative Path (NEG)"
)


# ---------------------------------------------------------------------------
# Element 5: output contract
# ---------------------------------------------------------------------------
OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["requirement_id", "reasoning", "tests"],
    "properties": {
        "requirement_id": {"type": "string"},
        "reasoning": {"type": "string"},
        "tests": {
            "type": "array",
            "minItems": 3,
            "items": {
                "type": "object",
                "required": ["name", "kind", "heuristic", "preconditions",
                             "actions", "expected", "trace"],
                "properties": {
                    "name": {"type": "string"},
                    "kind": {"type": "string", "enum": ["positive", "negative", "boundary"]},
                    "heuristic": {"type": "string", "enum": ["EP", "BVA", "STC", "DT", "NEG"]},
                    "preconditions": {"type": "array", "items": {"type": "string"}},
                    "actions": {"type": "array", "items": {"type": "string"}},
                    "expected": {"type": "array", "items": {"type": "string"}},
                    "trace": {"type": "array", "items": {"type": "string"}},
                    "executable": {"type": "string"},
                }
            }
        }
    }
}


def output_contract(target_framework: str) -> str:
    return (
        "[OUTPUT]\n"
        "Respond with VALID JSON ONLY conforming to the schema below. "
        "No prose outside the JSON. The `executable` field must contain "
        f"runnable {target_framework} source code for the test, ready to "
        "execute against the target system without modification.\n"
        f"Schema:\n{json.dumps(OUTPUT_SCHEMA, indent=2)}"
    )


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------
def compose_prompt(req: dict[str, Any], target_framework: str = "pytest",
                   glossary: dict[str, str] | None = None,
                   exemplars: list[dict[str, Any]] | None = None,
                   *, mode: str = "full") -> str:
    """Compose the full RAITG prompt.

    mode:
      "full"        — all five elements (RAITG)
      "no-heuristic" — ablation (drop element 4)
      "no-contract" — ablation (drop element 5)
      "naive"       — unverified-LLM baseline (just role + requirement)
    """
    if mode == "naive":
        return (
            f"You are a quality engineer. Write {target_framework} tests "
            f"for the requirement: {req['statement']}"
        )

    parts = [f"[ROLE]\n{ROLE_SENIOR_QA}", context_block(req, glossary, exemplars),
             task_directive(target_framework)]
    if mode != "no-heuristic":
        parts.append(HEURISTIC_SCAFFOLD)
    if mode != "no-contract":
        parts.append(output_contract(target_framework))
    return "\n\n".join(parts)


def repair_prompt(req: dict[str, Any], original: str,
                  rule_violations: list[str]) -> str:
    """Build a targeted repair prompt for verification failures.

    Supplies the original requirement, the failed response, and the
    specific violations so that the LLM can patch rather than
    regenerate from scratch.
    """
    return (
        "[ROLE]\n"
        + ROLE_SENIOR_QA +
        "\n\n[TASK]\nYour previous response failed rule-based verification. "
        "FIX every violation listed below while PRESERVING all tests that already pass. "
        "Do NOT discard the original structure. Do NOT emit an empty object. "
        "Do NOT wrap the JSON in markdown code fences or prose.\n\n"
        "[VIOLATIONS]\n- " + "\n- ".join(rule_violations) +
        "\n\n[ORIGINAL REQUIREMENT]\n" + json.dumps(req, indent=2) +
        "\n\n[YOUR PREVIOUS RESPONSE]\n" + original[:8000] +
        "\n\n[OUTPUT]\nRespond with VALID JSON ONLY conforming to the following schema. "
        "No prose, no code fences.\nSchema:\n"
        + json.dumps(OUTPUT_SCHEMA, indent=2)
    )
