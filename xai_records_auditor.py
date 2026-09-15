"""Audit the public-records request with xAI's Grok model."""

import argparse
import os
from pathlib import Path

from xai_sdk import Client
from xai_sdk.chat import system, user


MODEL = "grok-4.6"
SYSTEM_PROMPT = (
    "You are a legal research assistant auditing public records requests under "
    "Ohio R.C. 149.43. Identify factual or legal gaps, distinguish verified law "
    "from issues requiring current-source verification, and do not provide legal advice."
)


def audit_request(request_path: Path) -> str:
    """Submit the request text to Grok and return the compliance assessment."""
    if not os.getenv("XAI_API_KEY"):
        raise RuntimeError("XAI_API_KEY environment variable is required")
    if not request_path.is_file():
        raise FileNotFoundError(f"Request file not found: {request_path}")

    request_text = request_path.read_text(encoding="utf-8").strip()
    if not request_text:
        raise ValueError(f"Request file is empty: {request_path}")

    client = Client()
    chat = client.chat.create(
        model=MODEL,
        messages=[system(SYSTEM_PROMPT)],
    )
    chat.append(
        user(
            "Review the following PUBLIC_RECORDS_REQUEST.txt and verify its "
            "compliance for electronic transmission to a non-resident under Ohio "
            "R.C. 149.43(B)(7). Flag missing details and recommend corrections.\n\n"
            f"{request_text}"
        )
    )
    response = chat.sample()
    if not response.content:
        raise RuntimeError("The xAI model returned an empty response")
    return response.content.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit an Ohio public-records request with Grok")
    parser.add_argument(
        "request_path",
        nargs="?",
        type=Path,
        default=Path("PUBLIC_RECORDS_REQUEST.txt"),
        help="Path to the public-records request",
    )
    args = parser.parse_args()

    try:
        print(audit_request(args.request_path))
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())