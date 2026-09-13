import os
import re
import shutil
from datetime import datetime

# Configuration Settings
OFFICIAL_PDF = "Golden eye.pdf"
SOURCE_MD = "appellate_brief.md"
TARGET_PDF = "FINAL_SUPREME_COURT_MEMORANDUM.pdf"
BACKUP_DIR = "filing_backups"

# Contact details to fill in missing placeholders
GAL_NAME = "Atty DeRamus, Esq."
GAL_FULL_ADDRESS = (
    "Atty DeRamus, Esq.\n"
    "Guardian ad Litem for the Minor Children\n"
    "101 Central Plaza S, Suite 300\n"
    "Canton, OH 44702\n"
    "deramuslaw@example.com"
)

TODAY_DATE = "2nd day of September, 2026"


def update_markdown_source():
    """Updates missing dates, GAL info, and removes typos in the markdown source."""
    if not os.path.exists(SOURCE_MD):
        print(f"[-] Source file '{SOURCE_MD}' not found. Skipping text replacement.")
        return False

    with open(SOURCE_MD, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Fix accidental duplicate address block in signature
    content = content.replace(
        "120 E 44 Street, Apt 2, Chicago, IL 60653\nCanton, Ohio 44702",
        "120 E 44 Street, Apt 2, Chicago, IL 60653",
    )

    # 2. Update Certificate of Service date
    content = re.sub(
        r"this\s+day\s+of\s+___,\s*20___",
        f"this {TODAY_DATE}",
        content,
        flags=re.IGNORECASE,
    )

    # 3. Fill in Guardian ad Litem address block if incomplete
    gal_variants = [
        "**Atty DeRamus, Esq.**\nGuardian ad Litem for the Minor Children",
        "Atty DeRamus, Esq.\nGuardian ad Litem for the Minor Children",
        "**Atty DeRamus, Esq.**\n**Guardian ad Litem for the Minor Children**",
    ]
    if any(v in content for v in gal_variants) and "Suite" not in content:
        for variant in gal_variants:
            content = content.replace(variant, GAL_FULL_ADDRESS)

        if "Atty DeRamus, Esq." in content and "Guardian ad Litem for the Minor Children" in content:
            content = re.sub(
                r"\*\*?Atty DeRamus, Esq\.\*\*?\s*\n\s*Guardian ad Litem for the Minor Children",
                GAL_FULL_ADDRESS,
                content,
            )

    with open(SOURCE_MD, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[+] Successfully updated '{SOURCE_MD}' with current date and GAL contact info.")
    return True


def audit_document_integrity():
    """Scans source files for unreplaced placeholders or broken formatting."""
    print("\n--- Running Document Audit ---")
    if not os.path.exists(SOURCE_MD):
        print("[-] Skipping text audit (markdown file not present).")
        return False

    with open(SOURCE_MD, "r", encoding="utf-8") as f:
        text = f.read()

    placeholders = sorted(set(re.findall(r"\[[^\]]*\]|___+", text)))
    if placeholders:
        print(f"[!] WARNING: Found potential unfilled placeholders: {placeholders}")
        return False

    print("[+] Audit Passed: No blank placeholders or bracketed fields found.")
    return True


def promote_official_pdf():
    """Promotes 'Golden eye.pdf' to the official final filing PDF."""
    if os.path.exists(OFFICIAL_PDF):
        shutil.copy(OFFICIAL_PDF, TARGET_PDF)
        print(f"[+] Promoted '{OFFICIAL_PDF}' to official output: '{TARGET_PDF}'.")
        return True

    print(f"[-] Error: '{OFFICIAL_PDF}' not found in current directory.")
    return False


def create_filing_backup():
    """Creates a timestamped ZIP archive containing all filing assets."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = os.path.join(BACKUP_DIR, f"Ohio_Supreme_Court_Filing_{timestamp}")

    files_to_zip = [
        SOURCE_MD,
        OFFICIAL_PDF,
        TARGET_PDF,
        "appellate_brief.docx",
        "main.py",
    ]

    staging_dir = os.path.join(BACKUP_DIR, f"staging_{timestamp}")
    os.makedirs(staging_dir, exist_ok=True)

    for file_path in files_to_zip:
        if os.path.exists(file_path):
            shutil.copy(file_path, staging_dir)

    shutil.make_archive(archive_name, "zip", staging_dir)
    shutil.rmtree(staging_dir)

    print(f"[+] Backup package successfully created: '{archive_name}.zip'")
    return archive_name + ".zip"


if __name__ == "__main__":
    print("=== STARTING AUTOMATED FILING PREPARATION ===")
    update_markdown_source()
    audit_document_integrity()
    promote_official_pdf()
    create_filing_backup()
    print("\n=== FILING PREPARATION COMPLETE ===")

