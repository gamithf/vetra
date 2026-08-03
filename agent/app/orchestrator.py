"""Multi-agent orchestrator.

Runs the Vetra agent pipeline for one visit and streams real-time events
(thinking traces + tool actions) to the connected client.

Agents:
  1. Context   — loads patient context
  2. Medical   — streams Gemini reasoning over the transcript
  3. Notes     — saves the clinical note (raw + structured)
  4. Records   — writes the structured medical record
  5. Inventory — reconciles consumed items
  6. Billing   — generates the invoice line items
  7. Finalize  — marks the appointment completed
"""

import asyncio

from app.config import get_settings
from app.gemini import GeminiClient, VisitPlan
from app.tools import VetraTools

THINK_TICK = 0.035  # small pacing delay so streamed thinking reads naturally


async def _emit(emit, event: dict):
    await emit(event)


async def _think(emit, agent: str, text: str):
    # pace streaming chunks slightly so the UI shows progressive "thinking"
    for part in text.split(" "):
        await _emit(emit, {"type": "thinking", "agent": agent, "text": part + " "})
        await asyncio.sleep(THINK_TICK)


async def run_pipeline(emit, payload: dict):
    settings = get_settings()
    token = payload.get("token", "")
    pet_id = payload["pet_id"]
    appointment_id = payload["appointment_id"]
    vet_id = payload.get("vet_id")
    transcript = payload.get("transcript", "").strip()

    if not transcript:
        raise ValueError("transcript is required")

    tools = VetraTools(token)
    gemini = GeminiClient()

    # ── 1. Context agent ─────────────────────────────
    await _emit(emit, {"type": "agent", "agent": "context", "status": "working", "detail": "Loading patient context..."})
    pet = await tools.get_pet(pet_id)
    context = {
        "transcript": transcript,
        "pet_id": pet_id,
        "appointment_id": appointment_id,
        "vet_id": vet_id,
        "pet_name": pet.get("name", "the patient"),
        "species": pet.get("species", ""),
        "breed": pet.get("breed") or "",
        "gender": pet.get("gender", ""),
        "reason": payload.get("reason"),
    }
    await _emit(emit, {"type": "agent", "agent": "context", "status": "complete", "detail": f"Patient loaded: {context['pet_name']}"})

    # ── 2. Medical agent — live reasoning ────────────
    await _emit(emit, {"type": "agent", "agent": "medical", "status": "working", "detail": "Analyzing the consultation..."})
    async for chunk in gemini.stream_analysis(context):
        await _think(emit, "medical", chunk)
    await _emit(emit, {"type": "agent", "agent": "medical", "status": "complete", "detail": "Analysis complete"})

    # ── 3. Structured plan (single coordinated decision) ──
    plan: VisitPlan = await gemini.plan_visit(context)

    # ── 4. Notes agent — save raw + structured note ──
    await _emit(emit, {"type": "agent", "agent": "notes", "status": "thinking", "detail": "Structuring the clinical note..."})
    note_payload = {
        "pet_id": pet_id,
        "appointment_id": appointment_id,
        "raw_transcript": transcript,
        "structured_note": plan.structured_note,
        "ai_model_version": settings.GEMINI_MODEL,
        "status": "completed",
    }
    note = await tools.save_clinical_note(note_payload)
    await _emit(emit, {"type": "agent", "agent": "notes", "status": "complete", "detail": "Clinical note saved"})

    # ── 5. Records agent — write the medical record ──
    await _emit(emit, {"type": "agent", "agent": "records", "status": "thinking", "detail": "Writing the medical record..."})
    record_payload = {
        "pet_id": pet_id,
        "vet_id": vet_id,
        "appointment_id": appointment_id,
        "record_type": plan.record_type,
        "diagnosis": plan.diagnosis,
        "treatment": plan.treatment,
        "notes": plan.structured_note[:2000],
    }
    record = await tools.create_medical_record(record_payload)
    await _emit(emit, {"type": "agent", "agent": "records", "status": "complete", "detail": f"Diagnosis: {plan.diagnosis}"})

    # ── 6. Inventory agent — reconcile consumed items ──
    inventory = await tools.list_inventory()
    inventory_log = []
    for used in plan.inventory:
        item = VetraTools.match_inventory_item(inventory, used.item_name)
        if not item:
            await _emit(emit, {"type": "agent", "agent": "inventory", "status": "thinking", "detail": f"No stock match for \"{used.item_name}\" — skipping"})
            continue
        qty = max(1, int(used.quantity))
        await _emit(emit, {"type": "agent", "agent": "inventory", "status": "thinking", "detail": f"Consuming {qty} × {item['name']}..."})
        await tools.adjust_inventory(item["id"], -qty)
        inventory_log.append(f"{item['name']}: -{qty}")
    await _emit(emit, {"type": "agent", "agent": "inventory", "status": "complete", "detail": "Inventory updated" if inventory_log else "No inventory changes"})

    # ── 7. Billing agent — generate invoice ──
    await _emit(emit, {"type": "agent", "agent": "billing", "status": "thinking", "detail": "Calculating line items..."})
    invoice_items = [
        {"description": it.description, "quantity": it.quantity, "unit_price": it.unit_price}
        for it in plan.invoice_items
    ]
    invoice = await tools.create_invoice(appointment_id, invoice_items)
    total = invoice.get("total_amount", 0)
    await _emit(emit, {"type": "agent", "agent": "billing", "status": "complete", "detail": f"Bill generated: ${total:.2f}"})

    # ── 8. Finalize agent ────────────────────────────
    await _emit(emit, {"type": "agent", "agent": "finalize", "status": "working", "detail": "Marking the visit complete..."})
    await tools.complete_appointment(appointment_id)
    await _emit(emit, {"type": "agent", "agent": "finalize", "status": "complete", "detail": "Appointment completed"})

    await _emit(emit, {
        "type": "done",
        "summary": {
            "diagnosis": plan.diagnosis,
            "treatment": plan.treatment,
            "record_id": record.get("id"),
            "note_id": note.get("id"),
            "invoice_total": total,
            "inventory_log": inventory_log,
        },
    })
