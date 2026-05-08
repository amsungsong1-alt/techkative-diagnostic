"""
Tech-Kative AI-Readiness Diagnostic — Email Service

Sends two emails on submission:
  1. HTML report to the respondent
  2. Plain-text notification to the Tech-Kative inbox

Production: SMTP credentials from environment variables.
Local dev:  Falls back to writing .html files into ./outbox/ and logging.

Environment variables (set in .env or deployment secrets):
    SMTP_HOST        SMTP server hostname (e.g. smtp.gmail.com)
    SMTP_PORT        SMTP port (default 587 for STARTTLS)
    SMTP_USER        Login username
    SMTP_PASS        Login password
    FROM_ADDRESS     Sender address shown to recipients
    TECHKATIVE_INBOX Tech-Kative notification inbox address
"""

import logging
import os
import smtplib
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_OUTBOX = Path("outbox")


def _smtp_configured() -> bool:
    return all(
        os.environ.get(k)
        for k in ["SMTP_HOST", "SMTP_USER", "SMTP_PASS", "FROM_ADDRESS"]
    )


def _smtp_config() -> dict:
    return {
        "host":         os.environ["SMTP_HOST"],
        "port":         int(os.environ.get("SMTP_PORT", "587")),
        "user":         os.environ["SMTP_USER"],
        "password":     os.environ["SMTP_PASS"],
        "from_address": os.environ["FROM_ADDRESS"],
    }


# ---------------------------------------------------------------------------
# Core send helper
# ---------------------------------------------------------------------------

def _send_via_smtp(to_address: str, subject: str, html_body: str, text_body: str = "") -> None:
    cfg = _smtp_config()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = cfg["from_address"]
    msg["To"]      = to_address

    if text_body:
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(cfg["host"], cfg["port"]) as server:
        server.ehlo()
        server.starttls()
        server.login(cfg["user"], cfg["password"])
        server.sendmail(cfg["from_address"], [to_address], msg.as_string())


def _save_to_outbox(to_address: str, subject: str, html_body: str) -> Path:
    _OUTBOX.mkdir(exist_ok=True)
    slug = to_address.split("@")[0].replace(".", "_")
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid  = uuid.uuid4().hex[:6]
    filename = _OUTBOX / f"{ts}_{slug}_{uid}.html"
    filename.write_text(
        f"<!-- TO: {to_address} | SUBJECT: {subject} -->\n{html_body}",
        encoding="utf-8",
    )
    return filename


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def send_respondent_report(
    to_address: str,
    institution_name: str,
    tier: str,
    composite: float,
    report_html: str,
) -> bool:
    """
    Send the full HTML diagnostic report to the respondent.

    Returns True on success, False on failure (caller handles UI messaging).
    """
    subject = (
        f"Your AI-Readiness Diagnostic Report — {institution_name}"
    )

    intro = f"""
    <p style="font-family:sans-serif;color:#2d3454;font-size:15px;line-height:1.7;">
      Thank you for completing the Tech-Kative AI-Readiness Diagnostic.
      Your institution's profile is attached below.
      Your composite score is <strong>{composite:.0f} / 100</strong> —
      placing you at the <strong>{tier}</strong> tier.
    </p>
    <p style="font-family:sans-serif;color:#6b7290;font-size:14px;">
      If you would like to discuss your profile with a Tech-Kative advisor,
      please reply to this message or contact us at
      <a href="mailto:info@techkative.com">info@techkative.com</a>.
    </p>
    <hr style="border:none;border-top:1px solid #e2e4ee;margin:24px 0;">
    """

    full_html = report_html.replace(
        "<body>", f"<body>{intro}", 1
    )

    if _smtp_configured():
        try:
            _send_via_smtp(to_address, subject, full_html)
            logger.info("Respondent report sent to %s", to_address)
            return True
        except Exception as exc:
            logger.error("Failed to send respondent report: %s", exc)
            return False
    else:
        path = _save_to_outbox(to_address, subject, full_html)
        logger.info(
            "[LOCAL DEV] Respondent report saved to %s — configure SMTP env vars to send live email.",
            path,
        )
        return True


def send_techkative_notification(
    profile: dict,
    scores: dict,
) -> bool:
    """
    Send a plain-text notification to the Tech-Kative inbox.
    Contains institution name, tier, composite, and pillar breakdown.

    Returns True on success, False on failure.
    """
    inbox = os.environ.get("TECHKATIVE_INBOX", "")
    if not inbox and not _smtp_configured():
        # Local dev with no inbox configured — skip silently
        logger.info("[LOCAL DEV] TECHKATIVE_INBOX not set; skipping notification.")
        return True

    p           = scores["pillar_scores"]
    composite   = scores["composite"]
    tier        = scores["tier"]

    subject = (
        f"New Diagnostic Submission — {profile.get('institution_name', 'Unknown')} "
        f"[{tier}, {composite:.0f}]"
    )

    body_lines = [
        "New AI-Readiness Diagnostic submission received.",
        "",
        f"Institution:  {profile.get('institution_name', '')}",
        f"Type:         {profile.get('institution_type', '')}",
        f"Country:      {profile.get('country', '')}",
        f"Contact:      {profile.get('contact_name', '')} <{profile.get('contact_email', '')}>",
        f"Role:         {profile.get('role', '')}",
        "",
        f"Composite:    {composite:.0f} / 100  ({tier})",
        "",
        "Pillar scores:",
        f"  Governance & Policy:      {p['p1']:.0f}",
        f"  Data Foundations:         {p['p2']:.0f}",
        f"  Organisational Capacity:  {p['p3']:.0f}",
        f"  Ethical Infrastructure:   {p['p4']:.0f}",
    ]
    text_body = "\n".join(body_lines)
    html_body = "<pre style='font-family:monospace;font-size:13px;'>" + text_body + "</pre>"

    if _smtp_configured() and inbox:
        try:
            _send_via_smtp(inbox, subject, html_body, text_body)
            logger.info("Tech-Kative notification sent to %s", inbox)
            return True
        except Exception as exc:
            logger.error("Failed to send Tech-Kative notification: %s", exc)
            return False
    else:
        path = _save_to_outbox(inbox or "techkative-inbox", subject, html_body)
        logger.info(
            "[LOCAL DEV] Tech-Kative notification saved to %s",
            path,
        )
        return True


def send_all(
    profile: dict,
    scores: dict,
    report_html: str,
) -> tuple:
    """
    Convenience wrapper — sends both emails.
    Returns (respondent_ok: bool, notification_ok: bool).
    """
    respondent_ok = send_respondent_report(
        to_address=profile["contact_email"],
        institution_name=profile.get("institution_name", ""),
        tier=scores["tier"],
        composite=scores["composite"],
        report_html=report_html,
    )
    notification_ok = send_techkative_notification(profile, scores)
    return respondent_ok, notification_ok
