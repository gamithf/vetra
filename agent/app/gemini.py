"""Gemini 2.5 Flash client — streams live "thinking" and returns structured plans."""

import asyncio

from google import genai
from pydantic import BaseModel

from app.config import get_settings


class PlanInventoryItem(BaseModel):
    item_name: str
    quantity: int


class PlanInvoiceItem(BaseModel):
    description: str
    quantity: int
    unit_price: float


class VisitPlan(BaseModel):
    diagnosis: str
    treatment: str
    record_type: str = "examination"
    structured_note: str
    medications: list[str] = []
    inventory: list[PlanInventoryItem]
    invoice_items: list[PlanInvoiceItem]
    follow_up_in_days: int | None = None


class GeminiClient:
    def __init__(self):
        settings = get_settings()
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        self.model = settings.GEMINI_MODEL
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def _analysis_prompt(self, context: dict) -> str:
        return (
            "You are a senior veterinary AI assistant reasoning through a consultation "
            "for the Vetra clinic.\n\n"
            f"Patient: {context.get('pet_name')} ({context.get('species')}, "
            f"{context.get('breed') or 'unknown breed'}, {context.get('gender')})\n"
            f"Reason for visit: {context.get('reason') or 'Not specified'}\n\n"
            "Consultation transcript:\n"
            f"\"\"\"\n{context.get('transcript')}\n\"\"\"\n\n"
            "Think step by step out loud: summarize the presentation, note the key "
            "clinical findings, work toward a working diagnosis (state 'Healthy — no "
            "abnormalities found' if nothing is abnormal), and outline the recommended "
            "treatment and next steps. Be concise but complete."
        )

    def _plan_prompt(self, context: dict) -> str:
        return (
            "You are the Vetra clinical agents coordinator. Given the consultation "
            "below, produce a structured visit plan as JSON only.\n\n"
            "Rules:\n"
            "- diagnosis: one concise working diagnosis.\n"
            "- treatment: recommended treatment / plan text. If the transcript mentions "
            "a follow-up, include it (e.g. 'Schedule follow-up in 7 days').\n"
            "- follow_up_in_days: number of days until the follow-up visit (e.g. 7), "
            "or null if no follow-up is scheduled. Only set it when the transcript "
            "explicitly schedules a follow-up.\n"
            "- record_type: one of examination, vaccination, surgery, dental, "
            "lab_work, follow_up, emergency, other.\n"
            "- medications: list of drug names prescribed or dispensed during this "
            "visit, one entry per drug (e.g. 'Amoxicillin 250mg', 'Meloxicam 1.5mg'). "
            "Use the exact drug names as dictated; include the strength if given.\n"
            "- structured_note: a clean SOAP-style clinical note summarizing the visit.\n"
            "- inventory: the items consumed or dispensed during the visit. item_name "
            "should match clinic inventory naming exactly (e.g. 'Amoxicillin 250mg', "
            "'DAPP Vaccine', 'Syringes 3ml', 'Meloxicam 1.5mg'). Use whole-unit "
            "quantities. For a dispensed oral antibiotic course (e.g. 'Amoxicillin "
            "250mg') use 10 tablets (5-day course, BID). Vaccines and single-dose "
            "items use quantity 1. Only include items actually used or dispensed.\n"
            "- invoice_items: billable line items with description, quantity, and a "
            "realistic unit_price in Sri Lankan Rupees (LKR), rounded to whole rupees. "
            "Always include a consultation/examination fee line item (e.g. "
            "'Consultation Fee' Rs.500). Typical pricing: dermatology consult Rs.600, "
            "Amoxicillin 250mg Rs.25/tablet, lab work Rs.800.\n\n"
            f"Patient: {context.get('pet_name')} ({context.get('species')})\n"
            f"Reason for visit: {context.get('reason') or 'Not specified'}\n\n"
            "Transcript:\n"
            f"\"\"\"\n{context.get('transcript')}\n\"\"\"\n"
        )

    async def stream_analysis(self, context: dict):
        """Yield live text chunks as Gemini reasons through the case."""
        queue: asyncio.Queue = asyncio.Queue()
        prompt = self._analysis_prompt(context)

        def run():
            try:
                response = self.client.models.generate_content_stream(
                    model=self.model, contents=prompt
                )
                for chunk in response:
                    if chunk.text:
                        queue.put_nowait(chunk.text)
                queue.put_nowait(None)
            except Exception as exc:  # noqa: BLE001
                queue.put_nowait(exc)

        task = asyncio.get_running_loop().run_in_executor(None, run)
        while True:
            item = await queue.get()
            if item is None:
                break
            if isinstance(item, Exception):
                raise item
            yield item
        await task

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        t = text.strip()
        if t.startswith("```"):
            t = t.strip("`").strip()
            if t.lower().startswith("json"):
                t = t[4:].strip()
        return t

    async def plan_visit(self, context: dict) -> VisitPlan:
        prompt = self._plan_prompt(context)
        loop = asyncio.get_running_loop()

        def run():
            return self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": VisitPlan,
                },
            )

        resp = await loop.run_in_executor(None, run)

        parsed = getattr(resp, "parsed", None)
        if parsed is not None:
            return parsed if isinstance(parsed, VisitPlan) else VisitPlan.model_validate(parsed)

        text = (resp.text or "").strip()
        if not text and resp.candidates:
            parts = resp.candidates[0].content.parts
            text = "".join(getattr(p, "text", "") or "" for p in parts).strip()

        text = self._strip_code_fences(text)
        if not text:
            raise RuntimeError("Gemini returned an empty plan response")
        return VisitPlan.model_validate_json(text)
