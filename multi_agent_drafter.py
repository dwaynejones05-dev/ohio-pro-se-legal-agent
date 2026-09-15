"""Multi-agent legal drafting workflow powered by Google's GenAI SDK.

Set ``GEMINI_API_KEY`` before running this script. The workflow is advisory:
verify all legal authorities and facts with qualified counsel before filing.
"""

import argparse
import os
from pathlib import Path

from google import genai
from google.genai import types


MODEL = "gemini-2.5-flash"


def _generate(client: genai.Client, system_instruction: str, prompt: str) -> str:
    """Run one focused agent and return its text response."""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
        ),
    )
    if not response.text:
        raise RuntimeError("The Gemini agent returned an empty response")
    return response.text.strip()


def case_analyst_agent(case_facts: str, client: genai.Client | None = None) -> str:
    """Audit raw case notes for Fourth/Fourteenth Amendment and due-process issues."""
    active_client = client or genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _generate(
        active_client,
        """You are a careful constitutional-law issue spotter. Audit the supplied raw
case notes for potential Fourth Amendment, Fourteenth Amendment, and procedural
due-process violations. Separate facts from assumptions, identify missing facts,
and explain both supporting and weakening facts. Do not invent facts or declare
that a violation is proven. Organize the result with headings and a concise issue
summary suitable for a later legal drafting agent.""",
        f"RAW CASE NOTES:\n\n{case_facts}",
    )


def statute_checker_agent(claims: str, client: genai.Client | None = None) -> str:
    """Check legal claims against Ohio public-records law and Supreme Court rules."""
    active_client = client or genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _generate(
        active_client,
        """You are a meticulous Ohio legal authority checker. Review the proposed
claims below against Ohio Revised Code section 149.43 and the current Supreme Court
of Ohio Practice Rules. For every authority, distinguish quoted or verified law
from an item that requires current-source verification. Flag misstatements,
unsupported conclusions, procedural prerequisites, jurisdictional issues, and
missing citations. Never fabricate a rule number, quotation, deadline, or holding.
Return a structured verification report with suggested corrections.""",
        f"PROPOSED CLAIMS AND ANALYSIS:\n\n{claims}",
    )


def document_compiler_agent(
    analysis: str, citations: str, client: genai.Client | None = None
) -> str:
    """Compile the analysis and authority review into a polished Markdown filing."""
    active_client = client or genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _generate(
        active_client,
        """You are a senior legal editor drafting a polished Markdown court filing.
Combine the constitutional analysis and authority-check report below without
inventing facts or law. Use clear headings, numbered sections where appropriate,
neutral professional language, and bracketed placeholders for facts or citations
that the source material says are missing or unverified. Preserve uncertainty and
include a short verification checklist before filing. Do not present this draft as
legal advice or as proof that any constitutional violation occurred.""",
        "CONSTITUTIONAL ANALYSIS:\n\n"
        f"{analysis}\n\nAUTHORITY CHECK REPORT:\n\n{citations}",
    )


def _read_case_facts(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Case-facts file not found: {path}")
    case_facts = path.read_text(encoding="utf-8").strip()
    if not case_facts:
        raise ValueError(f"Case-facts file is empty: {path}")
    return case_facts


def main() -> int:
    parser = argparse.ArgumentParser(description="Draft a court filing with three Gemini agents")
    parser.add_argument(
        "case_facts",
        nargs="?",
        type=Path,
        default=Path("case_facts.txt"),
        help="Path to raw case notes (default: case_facts.txt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("compiled_filing.md"),
        help="Markdown output path (default: compiled_filing.md)",
    )
    args = parser.parse_args()

    if not os.getenv("GEMINI_API_KEY"):
        parser.error("GEMINI_API_KEY environment variable is required")

    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        case_facts = _read_case_facts(args.case_facts)
        analysis = case_analyst_agent(case_facts, client)
        citations = statute_checker_agent(analysis, client)
        filing = document_compiler_agent(analysis, citations, client)
        args.output.write_text(filing + "\n", encoding="utf-8")
    except (OSError, RuntimeError, ValueError) as error:
        parser.error(str(error))

    print(f"Compiled filing written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())