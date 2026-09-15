"""Generate a formal Notice of Appeal draft in Markdown.

This module creates a jurisdiction-neutral filing template. Review all bracketed
fields and confirm the applicable appellate rules before filing.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


@dataclass(frozen=True)
class AppealNoticeData:
    """Values used to populate a Notice of Appeal."""

    trial_court_name_division: str
    appellate_court_division: str
    plaintiffs: str
    defendants: str
    case_number: str
    trial_case_numbers: str
    appellant_name_role: str
    appellee_name: str
    judge_name: str
    order_date: str
    relief_requested: str
    pro_se_name: str
    pro_se_address: str
    pro_se_phone: str
    pro_se_email: str


def build_notice(data: AppealNoticeData) -> str:
    """Return a clean Markdown Notice of Appeal and proof-of-service template."""
    return f"""# NOTICE OF APPEAL

## IN THE SUPREME COURT OF OHIO

| **Dwayne Jones,** Appellant | **On Appeal from the {data.trial_court_name_division}** |
|:---|:---|
| v. | **Court of Appeals Case Nos.:** {data.case_number} |
| **{data.appellee_name},** Appellee | **Trial Court Case Nos.:** {data.trial_case_numbers} |
| | **Subject Matter:** {data.defendants} |

## NOTICE OF APPEAL

Notice is hereby given that **{data.appellant_name_role}** appeals to the
**{data.appellate_court_division}** from the order entered in this action on
**{data.order_date}**, signed by **{data.judge_name}**. This appeal is taken
from that order and any portion of the judgment reviewable with it under the
applicable rules.

The appellee is **{data.appellee_name}**.

The order being appealed is the decision of the **{data.judge_name}** in the
**{data.trial_court_name_division}**.

## PRAYER FOR RELIEF

The Appellant respectfully requests that the reviewing court **{data.relief_requested}**,
and grant such other relief as the court deems just and proper.

Respectfully submitted,

**{data.pro_se_name}**  
Pro Se Appellant  
{data.pro_se_address}  
Phone: {data.pro_se_phone}  
Email: {data.pro_se_email}

Date: ____________________

## FILING CHECKLIST

Based on the supplied filing information, the 45-day filing deadline is
**September 5, 2026**. Confirm the deadline and applicable requirements with
the Clerk of the Supreme Court of Ohio before filing. The jurisdictional
package should include:

- This Notice of Appeal.
- A Memorandum in Support of Jurisdiction.
- A date-stamped copy of the Court of Appeals decision.
- The $100 docket fee or an Affidavit of Indigence requesting a fee waiver.

---

# PROOF / CERTIFICATE OF SERVICE

I certify that on **____________________**, I served a true and correct copy
of this Notice of Appeal on the following person(s), using **____________________**
[method of service]:

**{data.appellee_name} / Counsel for Appellee**  
Name: __________________________________________  
Address: ________________________________________  
________________________________________________  
Email (if applicable): ____________________________

I declare that the foregoing is true and correct to the best of my knowledge.

Date: ____________________

Respectfully submitted,

**{data.pro_se_name}**  
Pro Se Appellant  
{data.pro_se_address}  
Phone: {data.pro_se_phone}  
Email: {data.pro_se_email}
"""


FIELD_DEFINITIONS = (
    ("trial_court_name_division", "Trial Court Name & Division"),
    ("appellate_court_division", "Appellate Court Division"),
    ("plaintiffs", "Plaintiff(s) Names"),
    ("defendants", "Defendant(s) Names"),
    ("case_number", "Case / Docket Number"),
    ("trial_case_numbers", "Trial Court Case Numbers"),
    ("appellant_name_role", "Appellant Name & Role"),
    ("appellee_name", "Appellee Name"),
    ("judge_name", "Judge Who Signed the Order"),
    ("order_date", "Date of the Order Being Appealed"),
    ("relief_requested", "Specific Relief Requested"),
    ("pro_se_name", "Pro Se Name"),
    ("pro_se_address", "Pro Se Mailing Address"),
    ("pro_se_phone", "Pro Se Phone"),
    ("pro_se_email", "Pro Se Email"),
)


def prompt_for_missing(
    values: dict[str, str | None], input_fn: Callable[[str], str] = input
) -> AppealNoticeData:
    """Prompt for omitted values and return the completed data object."""
    for field_name, label in FIELD_DEFINITIONS:
        if not values.get(field_name):
            values[field_name] = input_fn(f"{label}: ").strip()
        if not values[field_name]:
            raise ValueError(f"{label} is required")
    return AppealNoticeData(**{name: values[name] for name, _ in FIELD_DEFINITIONS})


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a formal Notice of Appeal Markdown draft."
    )
    for field_name, label in FIELD_DEFINITIONS:
        parser.add_argument(f"--{field_name.replace('_', '-')}", dest=field_name)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("notice_of_appeal.md"),
        help="Output Markdown path (default: notice_of_appeal.md)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> Path:
    parser = make_parser()
    args = parser.parse_args(argv)
    values = vars(args).copy()
    output_path = values.pop("output")
    data = prompt_for_missing(values)
    output_path.write_text(build_notice(data), encoding="utf-8")
    print(f"Notice of Appeal written to {output_path}")
    return output_path


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        raise SystemExit(str(error)) from error
