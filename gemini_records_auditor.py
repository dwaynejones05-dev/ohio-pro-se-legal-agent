import os
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=API_KEY)

def run_public_records_audit():
    print("=== OHIO PUBLIC RECORDS REQUEST AUDITOR ===")
    print("Initializing Gemini API Audit Engine...\n")

    audit_prompt = """
    You are an expert Ohio Public Records auditor evaluating requests under R.C. 149.43.
    Review the following statutory compliance areas for CPS/Children Services agency records:
    1. Redaction justification requirements (R.C. 149.43(B)(3)).
    2. Mandatory response timelines and 'promptness' standards.
    3. Identifying improperly withheld non-exempt agency logs, emails, and intake notes.

    Generate a concise audit checklist and response strategy for a pro se litigant.
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(audit_prompt)

        print("--- AUDIT RESULTS & STATUTORY FINDINGS ---")
        print(response.text)
        print("\n=== AUDIT COMPLETE ===")
    except Exception as error:
        print(f"Error executing audit: {error}")


if __name__ == "__main__":
    run_public_records_audit()
