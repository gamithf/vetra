"""
WhatsApp delivery test script — sends a test message and prints Meta's raw response.

This is the ground-truth check for whether a number can receive WhatsApp messages.

Usage (from backend/):
    python scripts/test_whatsapp.py [phone] [message...]

Default phone is the demo owner (Nuwan, 94707393930). Pass your own number to verify it.
Example:
    python scripts/test_whatsapp.py 94707123456 "Hello from Vetra test"
    python scripts/test_whatsapp.py 94707123456 Hello from Vetra test

How to read the result:
  - "sent: true"  -> Meta ACCEPTED the message (returned a wamid) and queued it for
                     delivery. Acceptance does NOT prove the handset received it.
  - Delivery proof = the phone actually buzzing. Meta never rejects/errors for an
                     unregistered WhatsApp number; it just silently never delivers.
  - "sent: false" -> Meta rejected it; the printed reason (and #code) tells you why
                     (e.g. #131030 = recipient not in the allowed test-number list).
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.config import get_settings  # noqa: E402
from app.services.whatsapp import normalize_phone, send_whatsapp_template, send_whatsapp_text  # noqa: E402


async def main() -> None:
    phone_arg = sys.argv[1] if len(sys.argv) > 1 else "94707393930"
    rest = sys.argv[2:]
    use_template = False
    if rest and rest[0] == "--template":
        use_template = True
        rest = rest[1:]
    message = " ".join(rest) if rest else None

    phone = normalize_phone(phone_arg)
    if not phone:
        print(f"✗ Cannot parse phone number {phone_arg!r} — expected E.164 (e.g. 9470XXXXXXX).")
        sys.exit(1)

    print(f"→ Testing phone: {phone_arg!r} (normalized to {phone})")

    if use_template:
        settings = get_settings()
        if not settings.AK_WHATSAPP__TEMPLATE_NAME:
            print("✗ No template to test — set AK_WHATSAPP__TEMPLATE_NAME in backend/.env first.")
            sys.exit(1)
        # Generic params for the 8-slot visit template (1..8).
        params = [message or f"Vetra test {datetime.now(timezone.utc).strftime('%H:%M:%S')}"]
        params.extend(["Test Pet", "ABCD1234", "Checkup"] + ["—"] * 2 + ["Rs.0.00", "https://example.com"])
        result = await send_whatsapp_template(phone, settings.AK_WHATSAPP__TEMPLATE_NAME, params)
    else:
        body = message or (
            "Vetra WhatsApp test — free-form text only delivers inside a 24h session. "
            f"Sent at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        result = await send_whatsapp_text(phone, body)

    print()
    print("RESULT:", result)
    print()
    if result.get("sent"):
        print("✓ Meta accepted the message (wamid returned) — it is queued for delivery.")
        if use_template:
            print("  An approved template delivers outside the 24h session, so check the")
            print("  phone now — if it arrived, template delivery is confirmed.")
        else:
            print("  Free-form only delivers inside a 24h user session; without one Meta")
            print("  holds the message and it will NOT arrive. Use --template to verify.")
    else:
        print(f"✗ Send failed: {result.get('reason')}")


if __name__ == "__main__":
    asyncio.run(main())
