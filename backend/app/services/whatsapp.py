"""WhatsApp Cloud API integration.

Uses the same Meta Graph endpoint as the standalone test script:
    POST https://graph.facebook.com/{version}/{phone_number_id}/messages
with a Bearer access token.
"""

import asyncio
import re

import httpx

from app.config import get_settings
from app.services.magic_link import create_pet_token

PHONE_RE = re.compile(r"\D")


def normalize_phone(raw: str | None) -> str | None:
    """Normalize a stored phone to E.164 digits suitable for WhatsApp.

    Handles local Sri Lankan formats (07XXXXXXXX, 07X XXX XXXX) and plain digits.
    Returns None if nothing usable is present.
    """
    if not raw:
        return None
    digits = PHONE_RE.sub("", raw)
    if len(digits) == 10 and digits.startswith("7"):
        return "94" + digits
    if len(digits) == 11 and digits.startswith("07"):
        return "94" + digits[1:]
    if len(digits) >= 10:
        return digits
    return None


def _whatsapp_error_hint(code, detail: str) -> str | None:
    """Friendly guidance for the most common Meta Cloud API send failures."""
    code = str(code)
    text = f"{detail}".lower()
    if code == "131030" or "not in allowed list" in text:
        return "Add this recipient number to the 'Recipient phone numbers' (test numbers) list in WhatsApp Manager."
    if code == "131047" or "re-engagement" in text:
        return "Free-form text only works inside a 24h user session. Send a template, or have the recipient message the business first."
    if code == "132000" or "not currently registered" in text:
        return "This number is not registered on WhatsApp (or has opted out)."
    if code in ("131026", "131042") or "phone number" in text and "not" in text:
        return "Check the phone number format — use E.164 with country code (e.g. 94XXXXXXXXX)."
    if "message" in text and "not allowed" in text:
        return "The message may violate WhatsApp policy for this number; use an approved template."
    return None


async def _post_message(settings, payload: dict, channel: str) -> dict:
    """POST a message payload to the Meta Graph API and parse the result.

    Meta confirms sends with a `messages[].id` in the body, and reports failures
    in the body too (sometimes with HTTP 200). Returns a dict with `sent`,
    `message_id` (on success) or `reason` (on failure) and a `_raw` key holding
    the original body for debugging.
    """
    url = f"https://graph.facebook.com/{settings.AK_WHATSAPP__API_VERSION}/{settings.AK_WHATSAPP__PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {settings.AK_WHATSAPP__ACCESS_TOKEN}", "Content-Type": "application/json"}

    print(f"POST {url}\nPayload: {payload}")

    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.post(url, json=payload, headers=headers)
        try:
            data = resp.json()
        except Exception:  # noqa: BLE001
            data = {}
        print(f"Meta response: {resp.status_code} {resp.text[:1000]}")

        # Success — Meta confirms with a `messages[].id` in the body.
        if resp.status_code == 200 and isinstance(data.get("messages"), list) and data["messages"]:
            return {
                "sent": True,
                "message_id": data["messages"][0].get("id"),
                "channel": channel,
                "_raw": data,
            }

        # Meta reports send failures in the body even with HTTP 200.
        error = data.get("error") or {}
        code = error.get("code")
        detail = error.get("message") or (resp.text or f"HTTP {resp.status_code}")
        hint = _whatsapp_error_hint(code, str(detail))
        reason = f"Meta API {resp.status_code}"
        if code:
            reason += f" (#{code})"
        reason += f": {str(detail)[:250]}"
        if hint:
            reason += f" — {hint}"
        return {"sent": False, "reason": reason[:600], "channel": channel, "_raw": data}
    except Exception as exc:  # noqa: BLE001
        return {"sent": False, "reason": str(exc)[:300], "channel": channel}


async def send_whatsapp_text(to: str, body: str) -> dict:
    """Send a plain-text WhatsApp message. Returns a result dict (never raises).

    Note: free-form text only delivers inside a 24h user-initiated session. For
    guaranteed delivery of business-initiated messages use an approved template
    (see send_whatsapp_template / send_visit_summary).
    """
    settings = get_settings()
    if not settings.AK_WHATSAPP__ACCESS_TOKEN or not settings.AK_WHATSAPP__PHONE_NUMBER_ID:
        return {"sent": False, "reason": "WhatsApp not configured (missing access token / phone number id)"}

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }

    return await _post_message(settings, payload, "text")


async def send_whatsapp_template(
    to: str,
    template_name: str,
    body_params: list[str] | None = None,
    language: str | None = None,
) -> dict:
    """Send a message via an APPROVED WhatsApp template (works outside the 24h window).

    `body_params` are bound in order to the template body's {{1}}, {{2}}, ... placeholders.
    """
    settings = get_settings()
    if not settings.AK_WHATSAPP__ACCESS_TOKEN or not settings.AK_WHATSAPP__PHONE_NUMBER_ID:
        return {"sent": False, "reason": "WhatsApp not configured (missing access token / phone number id)"}
    if not template_name:
        return {"sent": False, "reason": "No WhatsApp template name configured"}

    template = {
        "name": template_name,
        "language": {"code": language or settings.AK_WHATSAPP__TEMPLATE_LANGUAGE},
    }
    if body_params:
        template["components"] = [
            {
                "type": "body",
                "parameters": [{"type": "text", "text": p} for p in body_params],
            }
        ]

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "template",
        "template": template,
    }
    print(f"Sending WhatsApp template '{template_name}' to {to}")
    return await _post_message(settings, payload, "template")


async def send_visit_summary(
    appointment,
    pet,
    owner,
    invoice,
    invoice_items,
    diagnosis: str | None = None,
    treatment: str | None = None,
) -> dict:
    """Build and send the owner WhatsApp message for a completed visit.

    Message contains the visit id, description, the bill total/link and a magic
    link to the secure public pet web view. Best-effort: never raises, returns a
    result dict the caller can surface in the pipeline.
    """
    settings = get_settings()
    phone = normalize_phone(owner.phone if owner else None)
    if not phone:
        return {"sent": False, "reason": f"Owner has no usable phone number (stored: {owner.phone if owner else None!r})"}

    token = create_pet_token(pet.id)
    page_url = f"{settings.FRONTEND_URL.rstrip('/')}/p/{token}"

    owner_first = (owner.first_name if owner else "there")
    pet_name = pet.name
    visit_id = str(appointment.id)[:8].upper()
    reason = appointment.reason or "Visit"
    total = invoice.total_amount if invoice else 0
    total_line = f"Rs.{total:,.2f}" if invoice else None

    def freeform_lines() -> list[str]:
        lines = [
            f"Your pet {pet_name} has completed their visit at Vetra.",
            "",
            f"Visit ID: #{visit_id}",
            f"Reason: {reason}",
        ]
        if diagnosis:
            lines.append(f"Diagnosis: {diagnosis}")
        if treatment:
            lines.append(f"Treatment: {treatment}")
        lines.extend([
            "",
            f"Total: {total_line}" if total_line else "Bill available at the clinic",
            "",
            f"View {pet_name}'s visit details and bill:",
            page_url,
        ])
        return lines

    # If an approved template is configured, send via the template (works outside
    # the 24h session — the reliable path for business-initiated messages). If the
    # template send is rejected, or no template is configured, fall back to free-form
    # text (which only delivers inside a 24h user session).
    if settings.AK_WHATSAPP__TEMPLATE_NAME:
        body_params = [
            owner_first,
            pet_name,
            visit_id,
            reason,
            diagnosis or "Not recorded",
            treatment or "Not recorded",
            total_line or "Available at the clinic",
            page_url,
        ]
        result = await send_whatsapp_template(
            phone, settings.AK_WHATSAPP__TEMPLATE_NAME, body_params, settings.AK_WHATSAPP__TEMPLATE_LANGUAGE
        )
        if result.get("sent"):
            return result
        # Template rejected (e.g. not yet approved / wrong name) — try free-form.
        return await send_whatsapp_text(phone, "\n".join(freeform_lines()))

    return await send_whatsapp_text(phone, "\n".join(freeform_lines()))
