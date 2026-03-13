"""OTP utilities for CSPC email verification via Azure Communication Services."""

from __future__ import annotations

import hashlib
import os
import secrets
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

try:
    from azure.communication.email import EmailClient

    ACS_AVAILABLE = True
except Exception:
    ACS_AVAILABLE = False


def _get_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        parsed = int(raw)
        return parsed if parsed > 0 else default
    except ValueError:
        return default


OTP_EXPIRY_MINUTES = _get_int_env("OTP_EXPIRY_MINUTES", 5)
OTP_MAX_ATTEMPTS = _get_int_env("OTP_MAX_ATTEMPTS", 5)
OTP_RESEND_COOLDOWN_SECONDS = _get_int_env("OTP_RESEND_COOLDOWN_SECONDS", 60)


@dataclass
class OTPRecord:
    otp_hash: str
    expires_at: datetime
    attempts: int
    resend_available_at: datetime


# In-memory OTP store: {email: OTPRecord}. This resets when the app restarts.
_OTP_STORE: Dict[str, OTPRecord] = {}
_OTP_LOCK = threading.Lock()


def _normalize_email(email: Optional[str]) -> str:
    return (email or "").strip().lower()


def is_cspc_email(email: Optional[str]) -> bool:
    """Validate if email belongs to approved CSPC domains."""
    value = _normalize_email(email)
    return value.endswith("@cspc.edu.ph") or value.endswith("@my.cspc.edu.ph")


def _hash_otp(otp: str) -> str:
    salt = os.getenv("OTP_HASH_SALT", "eduroom-otp-salt")
    return hashlib.sha256(f"{salt}:{otp}".encode("utf-8")).hexdigest()


def _generate_otp(length: int = 6) -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def _get_email_client() -> Tuple[Optional[EmailClient], Optional[str], Optional[str]]:
    connection_string = os.getenv("ACS_CONNECTION_STRING")
    sender = os.getenv("ACS_SENDER_EMAIL")

    if not connection_string:
        return None, None, "ACS_CONNECTION_STRING is not configured."
    if not sender:
        return None, None, "ACS_SENDER_EMAIL is not configured."
    if not ACS_AVAILABLE:
        return None, None, "azure-communication-email package is missing."

    try:
        client = EmailClient.from_connection_string(connection_string)
    except Exception as ex:
        return None, None, f"Unable to initialize email client: {str(ex)}"

    return client, sender, None


def _seconds_until(target: datetime, now: datetime) -> int:
    return max(int((target - now).total_seconds()), 0)


def _build_otp_message(sender: str, recipient: str, otp: str) -> dict:
    plain_text = (
        "EduROOM - CSPC Email Verification\n\n"
        f"Your one-time password (OTP) is: {otp}\n"
        f"This code will expire in {OTP_EXPIRY_MINUTES} minutes.\n\n"
        "If you did not request this code, you can safely ignore this message."
    )

    html = f"""
<!doctype html>
<html lang=\"en\">
    <body style=\"margin:0;padding:0;background-color:#f3f7fb;font-family:Arial,Helvetica,sans-serif;color:#1f2937;\">
        <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"background-color:#f3f7fb;padding:24px 12px;\">
            <tr>
                <td align=\"center\">
                    <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"max-width:560px;background:#ffffff;border:1px solid #dbe4ef;border-radius:12px;overflow:hidden;\">
                        <tr>
                            <td style=\"background:#2e6fa3;padding:18px 24px;color:#ffffff;font-size:18px;font-weight:700;\">
                                EduROOM Verification
                            </td>
                        </tr>
                        <tr>
                            <td style=\"padding:24px;\">
                                <p style=\"margin:0 0 12px 0;font-size:14px;line-height:1.6;\">Hello,</p>
                                <p style=\"margin:0 0 14px 0;font-size:14px;line-height:1.6;\">
                                    Use the one-time password below to verify your CSPC email and continue signing in.
                                </p>
                                <table role=\"presentation\" cellspacing=\"0\" cellpadding=\"0\" style=\"margin:8px 0 16px 0;\">
                                    <tr>
                                        <td style=\"background:#f5f9fd;border:1px solid #c9d9ea;border-radius:10px;padding:12px 18px;font-size:30px;line-height:1;font-weight:700;letter-spacing:6px;color:#1f2937;text-align:center;\">
                                            {otp}
                                        </td>
                                    </tr>
                                </table>
                                <p style=\"margin:0 0 8px 0;font-size:13px;line-height:1.6;color:#4b5563;\">
                                    Expires in <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.
                                </p>
                                <p style=\"margin:0;font-size:12px;line-height:1.6;color:#6b7280;\">
                                    If you did not request this code, please ignore this email.
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td style=\"padding:14px 24px;background:#f9fbfd;border-top:1px solid #e5edf5;font-size:11px;line-height:1.5;color:#6b7280;\">
                                This is an automated message from EduROOM. Do not reply to this email.
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
</html>
"""

    return {
        "senderAddress": sender,
        "recipients": {"to": [{"address": recipient}]},
        "content": {
            "subject": "EduROOM | Your CSPC Verification Code",
            "plainText": plain_text,
            "html": html,
        },
    }


def send_otp_email(email: Optional[str]) -> Tuple[bool, str]:
    recipient = _normalize_email(email)
    if not is_cspc_email(recipient):
        return False, "Only CSPC email addresses are allowed."

    now = datetime.utcnow()
    with _OTP_LOCK:
        existing = _OTP_STORE.get(recipient)
        if existing and now < existing.resend_available_at:
            seconds_left = _seconds_until(existing.resend_available_at, now)
            return False, f"Please wait {seconds_left}s before requesting another OTP."

    client, sender, error = _get_email_client()
    if error:
        return False, error

    otp = _generate_otp()
    otp_hash = _hash_otp(otp)
    expires_at = now + timedelta(minutes=OTP_EXPIRY_MINUTES)
    message = _build_otp_message(sender, recipient, otp)

    try:
        poller = client.begin_send(message)
        poller.result()
    except Exception as ex:
        return False, f"Failed to send OTP email: {str(ex)}"

    with _OTP_LOCK:
        _OTP_STORE[recipient] = OTPRecord(
            otp_hash=otp_hash,
            expires_at=expires_at,
            attempts=0,
            resend_available_at=now + timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS),
        )

    return True, "OTP sent. Please check your email."


def verify_otp(email: Optional[str], otp: Optional[str]) -> Tuple[bool, str]:
    recipient = _normalize_email(email)
    code = (otp or "").strip()

    if not recipient or not code:
        return False, "Email and OTP are required."

    now = datetime.utcnow()
    with _OTP_LOCK:
        record = _OTP_STORE.get(recipient)
        if not record:
            return False, "No OTP request found. Please request a new code."

        if now > record.expires_at:
            _OTP_STORE.pop(recipient, None)
            return False, "OTP expired. Please request a new code."

        record.attempts += 1
        if record.attempts > OTP_MAX_ATTEMPTS:
            _OTP_STORE.pop(recipient, None)
            return False, "Too many invalid attempts. Please request a new code."

        if _hash_otp(code) != record.otp_hash:
            tries_left = OTP_MAX_ATTEMPTS - record.attempts
            return False, f"Invalid OTP. Attempts left: {max(tries_left, 0)}"

        _OTP_STORE.pop(recipient, None)

    return True, "OTP verified."
