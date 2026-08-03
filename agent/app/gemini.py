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
    inventory: list[PlanInventoryItem]
    invoice_items: list[PlanInvoiceItem]


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
            "- treatment: recommended treatment / plan text.\n"
            "- record_type: one of examination, vaccination, surgery, dental, "
            "lab_work, follow_up, emergency, other.\n"
            "- structured_note: a clean SOAP-style clinical note summarizing the visit.\n"
            "- inventory: the items consumed during the visit (vaccines, medications, "
            "supplies). item_name should match the clinic inventory naming as closely "
            "as possible (e.g. 'DAPP Vaccine', 'Syringes 3ml', 'Gauze'). Use quantity "
            "in whole units actually used.\n"
            "- invoice_items: the billable line items (consultation, examination, "
            "vaccines, medications, procedures). Provide description, quantity, and a "
            "realistic unit_price in USD. Always include a consultation/examination fee.\n\n"
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

    async def plan_visit(self, context: dict) -> VisitPlan:
        prompt = self._plan_prompt(context)
        loop = asyncio.get_running_loop()

        def run():
            resp = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": VisitPlan,
                },
            )
            return resp.text

        text = await loop.run_in_executor(None, run)
        return VisitPlan.model_validate_json(text)
