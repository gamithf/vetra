"""Tools the agents use to perform real actions against the Vetra backend API.

Every tool is authenticated with the calling user's JWT, so role-based
permissions from the main application are preserved.
"""

import httpx

from app.config import get_settings


class VetraAPIError(RuntimeError):
    pass


class VetraTools:
    def __init__(self, token: str):
        self.base = get_settings().VETRA_API_URL.rstrip("/")
        self.token = token

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    async def _call(self, method: str, path: str, **kwargs):
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            resp = await client.request(
                method, f"{self.base}{path}", headers=self._headers(), **kwargs
            )
        if resp.status_code >= 400:
            detail = resp.text[:400] if resp.text else resp.status_code
            raise VetraAPIError(f"Vetra API {method} {path} -> {resp.status_code}: {detail}")
        if not resp.content:
            return {}
        return resp.json()

    async def get_pet(self, pet_id: str) -> dict:
        return await self._call("GET", f"/pets/{pet_id}")

    async def save_clinical_note(self, payload: dict) -> dict:
        return await self._call("POST", "/clinical-notes", json=payload)

    async def create_medical_record(self, payload: dict) -> dict:
        return await self._call("POST", "/medical-records", json=payload)

    async def list_inventory(self) -> list:
        return await self._call("GET", "/inventory")

    async def adjust_inventory(self, item_id: str, change: int) -> dict:
        return await self._call(
            "POST", f"/inventory/{item_id}/adjust", params={"quantity_change": change}
        )

    async def create_invoice(self, appointment_id: str, items: list[dict]) -> dict:
        return await self._call(
            "POST",
            f"/appointments/{appointment_id}/create-invoice",
            json={"items": items},
        )

    async def get_invoice_for_appointment(self, appointment_id: str) -> dict | None:
        """Return the existing invoice for an appointment, or None if none exists."""
        try:
            return await self._call("GET", f"/invoices/by-appointment/{appointment_id}")
        except VetraAPIError as exc:
            if "404" in str(exc):
                return None
            raise

    async def complete_appointment(self, appointment_id: str) -> dict:
        return await self._call("POST", f"/appointments/{appointment_id}/complete")

    @staticmethod
    def match_inventory_item(inventory: list, wanted_name: str):
        """Case-insensitive fuzzy match of an item name against clinic inventory."""
        wanted = wanted_name.strip().lower()
        if not wanted:
            return None
        for item in inventory:
            if item["name"].lower() == wanted:
                return item
        for item in inventory:
            if wanted in item["name"].lower() or item["name"].lower() in wanted:
                return item
        return None
