"""Send the Ohio public-records request by email.

Required environment variables:
    SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD

The script uses STARTTLS by default. Set SMTP_USE_SSL=true for an implicit
TLS connection, such as the usual SMTP configuration on port 465.
"""

import logging
import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path


RECIPIENT = "police.records@cantonohio.gov"
CC_RECIPIENT = "tami.ketler@cantonohio.gov"
REQUEST_FILENAME = "PUBLIC_RECORDS_REQUEST.txt"
PIPELINE_LOG_FILENAME = "pipeline_log.txt"
REQUIRED_CITATION = "R.C. 149.43(B)(7)"

LOGGER = logging.getLogger("send_records_request")


def configure_logging() -> None:
    """Configure timestamped console logging for a command-line run."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )


def load_smtp_settings() -> tuple[str, int, str, str, bool]:
    """Load and validate SMTP settings without exposing the password."""
    missing = [
        name
        for name in ("SMTP_SERVER", "SMTP_PORT", "SENDER_EMAIL", "SENDER_PASSWORD")
        if not os.getenv(name)
    ]
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): " + ", ".join(missing)
        )

    try:
        port = int(os.environ["SMTP_PORT"])
    except ValueError as error:
        raise RuntimeError("SMTP_PORT must be an integer") from error

    if not 1 <= port <= 65535:
        raise RuntimeError("SMTP_PORT must be between 1 and 65535")

    use_ssl = os.getenv("SMTP_USE_SSL", "false").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    return (
        os.environ["SMTP_SERVER"],
        port,
        os.environ["SENDER_EMAIL"],
        os.environ["SENDER_PASSWORD"],
        use_ssl,
    )


def read_request(request_path: Path) -> tuple[str, str]:
    """Read the request and derive a subject from its optional header."""
    if not request_path.is_file():
        raise FileNotFoundError(f"Request file not found: {request_path}")

    content = request_path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"Request file is empty: {request_path}")

    subject = "Public Records Request - R.C. 149.43(B)(7)"
    body = content
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.upper().startswith("SUBJECT:"):
            subject = line.split(":", 1)[1].strip()
            body = "\n".join(lines[index + 1 :]).strip()
            break

    if REQUIRED_CITATION not in subject and REQUIRED_CITATION not in body:
        body = f"Pursuant to {REQUIRED_CITATION}.\n\n{body}"

    return subject, body


def append_pipeline_log(log_path: Path, sender: str, subject: str) -> None:
    """Record successful delivery metadata in the pipeline log."""
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    entry = (
        f"{timestamp} SUCCESS public-records email sent "
        f"from={sender} to={RECIPIENT} cc={CC_RECIPIENT} subject={subject}\n"
    )
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(entry)


def send_records_request(repository_root: Path | None = None) -> None:
    """Read, format, and send the public-records request."""
    root = repository_root or Path(__file__).resolve().parent
    request_path = root / REQUEST_FILENAME
    log_path = root / PIPELINE_LOG_FILENAME
    server, port, sender, password, use_ssl = load_smtp_settings()
    subject, body = read_request(request_path)

    message = EmailMessage()
    message["From"] = sender
    message["To"] = RECIPIENT
    message["Cc"] = CC_RECIPIENT
    message["Subject"] = subject
    message.set_content(body)
    recipients = [RECIPIENT, CC_RECIPIENT]

    LOGGER.info("Preparing public-records request from %s", request_path)
    LOGGER.info("Sending email to %s with CC %s via %s:%s", RECIPIENT, CC_RECIPIENT, server, port)
    context = ssl.create_default_context()
    smtp_connection: smtplib.SMTP | smtplib.SMTP_SSL
    try:
        if use_ssl:
            smtp_connection = smtplib.SMTP_SSL(server, port, context=context, timeout=30)
        else:
            smtp_connection = smtplib.SMTP(server, port, timeout=30)

        with smtp_connection as smtp:
            smtp.ehlo()
            if not use_ssl:
                smtp.starttls(context=context)
                smtp.ehlo()
            smtp.login(sender, password)
            smtp.send_message(message, from_addr=sender, to_addrs=recipients)
    except (OSError, smtplib.SMTPException) as error:
        LOGGER.exception("Public-records email failed: %s", error)
        raise RuntimeError("Unable to send the public-records email") from error

    append_pipeline_log(log_path, sender, subject)
    LOGGER.info("Email sent successfully; pipeline log updated at %s", log_path)


def main() -> int:
    configure_logging()
    try:
        send_records_request()
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        LOGGER.error("Public-records request was not sent: %s", error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())