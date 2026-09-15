"""
Ohio Pro Se Multi-Agent Legal Drafter
- Agents powered by Gemini with Brian Steel mindset (relentless, meticulous, creative, winning grit)
- Includes a rigorous Judge Review agent
- Full pipeline: Draft → Judge → Auto-Revise
"""

import argparse
import os
from pathlib import Path

from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"

# ------------------------------------------------------------------
# Core helper
# ------------------------------------------------------------------
def _generate(client: genai.Client, system_instruction: str, prompt: str) -> str:
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

# ------------------------------------------------------------------
# Brian Steel Mindset Agents
# ------------------------------------------------------------------
STEEL_CORE = """
You operate with the mindset and grit of elite appellate/trial lawyer Brian Steel:
- Exhaustive preparation is non-negotiable.
- Find every viable argument, novel angle, and procedural lever.
- Fight every point that can help the client. Never surrender early.
- Write with precision, force, clarity, and professional confidence.
- Anticipate and neutralize the Court’s and opposing side’s strongest attacks.
- Never invent facts or law. Clearly mark anything that still needs verification.
"""

def case_analyst_agent(case_facts: str, client: genai.Client) -> str:
    system = STEEL_CORE + """
You are a relentless constitutional and appellate issue-spotter.
Audit the raw case notes for every viable Fourth Amendment, Fourteenth Amendment,
due-process, and procedural claim under Ohio and federal law.
Separate hard facts from assumptions. Identify missing facts that must be obtained.
Highlight both supporting and weakening evidence. Look for creative leverage points.
Organize the result with clear headings so a later drafting agent can turn them into winning arguments.
"""
    return _generate(client, system, f"RAW CASE NOTES:\n\n{case_facts}")

def statute_checker_agent(claims: str, client: genai.Client) -> str:
    system = STEEL_CORE + """
You are a meticulous Ohio authority and appellate specialist.
Verify every claim against the Ohio Revised Code (especially R.C. 149.43),
Supreme Court of Ohio Practice Rules, and controlling case law.
Flag unsupported statements, missing prerequisites, jurisdictional traps, and weak citations.
Suggest stronger or alternative authorities and creative procedural moves.
Return a structured verification + improvement report.
"""
    return _generate(client, system, f"PROPOSED CLAIMS AND ANALYSIS:\n\n{claims}")

def document_compiler_agent(analysis: str, citations: str, client: genai.Client) -> str:
    system = STEEL_CORE + """
You are a senior appellate drafter.
Produce a polished, forceful Markdown court filing that combines the analysis and authority report.
Use clear structure, strong but professional language, and anticipatory responses to likely judicial attacks.
Insert bracketed placeholders only where verification is still required.
Make every argument count. End with a short internal verification checklist.
Do not claim this is legal advice or that any violation is proven.
"""
    prompt = (
        "CONSTITUTIONAL ANALYSIS:\n\n"
        f"{analysis}\n\n"
        "AUTHORITY CHECK REPORT:\n\n"
        f"{citations}"
    )
    return _generate(client, system, prompt)

# ------------------------------------------------------------------
# Judge Agent
# ------------------------------------------------------------------
def judge_review_agent(filing_text: str, client: genai.Client) -> str:
    system = """
You are a highly experienced Ohio appellate and Supreme Court judge with 25+ years on the bench.
You are fair, precise, and extremely demanding. You have reviewed thousands of filings.

Review the submitted filing and provide a structured, blunt assessment:

1. Overall Impression (1-2 sentences)
2. Procedural & Technical Compliance (Ohio Appellate Rules / Supreme Court Practice Rules, formatting, service, jurisdiction, etc.)
3. Legal Strengths
4. Legal Weaknesses & Vulnerabilities (every soft spot the Court or opposing side will attack)
5. Persuasion & Clarity
6. Specific Suggestions for Improvement (concrete and prioritized)
7. Realistic Judicial Outlook
8. Priority Fixes (top 3–5 items only)

Be direct and professional. Never invent facts or law. Do not give legal advice.
"""
    return _generate(client, system, f"FILING TO REVIEW:\n\n{filing_text}")

# ------------------------------------------------------------------
# Revision Agent (applies Judge feedback)
# ------------------------------------------------------------------
def reviser_agent(original_filing: str, judge_feedback: str, client: genai.Client) -> str:
    system = STEEL_CORE + """
You are a senior appellate reviser with Brian Steel’s relentless standards.
Take the original filing and the Judge’s feedback.
Produce a significantly improved Markdown version that incorporates the Priority Fixes and other valid suggestions.
Keep the same professional, forceful tone. Do not invent new facts or law.
Clearly mark any remaining items that still need human verification.
"""
    prompt = (
        "ORIGINAL FILING:\n\n"
        f"{original_filing}\n\n"
        "JUDGE FEEDBACK:\n\n"
        f"{judge_feedback}\n\n"
        "Produce the revised filing now."
    )
    return _generate(client, system, prompt)

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _read_file(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"File is empty: {path}")
    return text

# ------------------------------------------------------------------
# Main pipeline
# ------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Steel-mindset multi-agent drafter + Judge review for Ohio pro se filings"
    )
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
        help="Draft output path (default: compiled_filing.md)",
    )
    args = parser.parse_args()

    if not os.getenv("GEMINI_API_KEY"):
        parser.error("GEMINI_API_KEY environment variable is required")

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    print("=== STARTING STEEL-MINDSET DRAFTING PIPELINE ===\n")

    # 1. Read case facts
    case_facts = _read_file(args.case_facts)
    print("[1/5] Case facts loaded")

    # 2. Case Analyst
    print("[2/5] Running Case Analyst (Steel mindset)...")
    analysis = case_analyst_agent(case_facts, client)

    # 3. Statute Checker
    print("[3/5] Running Statute / Authority Checker...")
    citations = statute_checker_agent(analysis, client)

    # 4. Document Compiler
    print("[4/5] Compiling polished filing...")
    filing = document_compiler_agent(analysis, citations, client)
    args.output.write_text(filing + "\n", encoding="utf-8")
    print(f"    → Draft saved to: {args.output}")

    # 5. Judge Review
    print("[5/5] Running Judge Review Agent...")
    judge_feedback = judge_review_agent(filing, client)
    judge_path = Path("judge_review.md")
    judge_path.write_text(judge_feedback + "\n", encoding="utf-8")
    print(f"    → Judge review saved to: {judge_path}")

    # 6. Auto-revise based on Judge feedback
    print("\n[Bonus] Applying Judge’s Priority Fixes → creating revised version...")
    revised = reviser_agent(filing, judge_feedback, client)
    revised_path = Path("revised_filing.md")
    revised_path.write_text(revised + "\n", encoding="utf-8")
    print(f"    → Revised filing saved to: {revised_path}")

    print("\n=== PIPELINE COMPLETE ===")
    print("Files created:")
    print(f"  • {args.output}          (original Steel draft)")
    print(f"  • judge_review.md       (judicial critique)")
    print(f"  • revised_filing.md     (improved version)")
    print("\nReview the Judge’s Priority Fixes carefully before using any filing.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
