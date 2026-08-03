from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    owners,
    pets,
    rooms,
    appointments,
    medical_records,
    vaccinations,
    lab_results,
    clinical_notes,
    inventory,
    prescriptions,
    invoices,
    weight_records,
    dashboard,
    transcription,
)

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(owners.router)
router.include_router(pets.router)
router.include_router(rooms.router)
router.include_router(appointments.router)
router.include_router(medical_records.router)
router.include_router(vaccinations.router)
router.include_router(lab_results.router)
router.include_router(clinical_notes.router)
router.include_router(inventory.router)
router.include_router(prescriptions.router)
router.include_router(invoices.router)
router.include_router(weight_records.router)
router.include_router(dashboard.router)
router.include_router(transcription.router)
