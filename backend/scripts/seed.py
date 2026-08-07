"""
Database seed script — populates Vetra with sample data for development/demo.

Usage:
    cd backend
    python scripts/seed.py
"""

import asyncio
import sys
from pathlib import Path

# Ensure the backend root is on sys.path so `app` is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Make seed output safe on Windows consoles (cp1252) — emoji/check marks would crash otherwise.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import uuid
from datetime import datetime, timezone, timedelta, date

import bcrypt
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from app.config import get_settings
from app.models import *  # noqa: F401, F403
from app.enums import *  # noqa: F401, F403


settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def hashpw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def dt(offset_days: int = 0, hour: int = 9, minute: int = 0) -> datetime:
    """Return a timezone-aware datetime relative to today."""
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return today + timedelta(days=offset_days, hours=hour, minutes=minute)


# ──────────────────────────────────────────────
# Seed data
# ──────────────────────────────────────────────

async def seed(session: AsyncSession):
    # Clear existing data so re-running the seed always produces a fresh demo DB.
    for table in reversed(SQLModel.metadata.sorted_tables):
        await session.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))
    await session.commit()
    print("  🧹 Cleared existing data")

    # ── Rooms ──────────────────────────────
    rooms_data = [
        {"name": "Exam Room 1", "number": 101},
        {"name": "Exam Room 2", "number": 102},
        {"name": "Exam Room 3", "number": 103},
        {"name": "Surgery Suite", "number": 201},
        {"name": "Dental Suite", "number": 202},
        {"name": "Isolation Ward", "number": 301},
    ]
    rooms = [Room(**r) for r in rooms_data]
    session.add_all(rooms)
    await session.flush()
    print(f"  ✓ {len(rooms)} rooms")

    # ── Users ──────────────────────────────
    avatar = lambda slug: f"https://api.dicebear.com/10.x/open-peeps/svg?seed={slug}"
    users_data = [
        {"email": "vet1@vetra.com",   "password": "@password123PP", "full_name": "Dr. Kasun Perera",       "role": UserRole.VET,    "phone": "070-1010-001", "photo_url": avatar("t9ce14in")},
        {"email": "vet2@vetra.com",  "password": "@password123PP", "full_name": "Dr. Nadeesha Fernando",    "role": UserRole.VET,    "phone": "070-1010-002", "photo_url": avatar("Nadeesha")},
        {"email": "vet3@vetra.com",  "password": "@password123PP", "full_name": "Dr. Ruwan Bandara",        "role": UserRole.VET,    "phone": "070-1010-003", "photo_url": avatar("Ruwan")},
        {"email": "staff1@vetra.com", "password": "@password123PP", "full_name": "Ishara Kumari",           "role": UserRole.STAFF,  "phone": "070-1020-001", "photo_url": avatar("ulxpijvx")},
        {"email": "staff2@vetra.com","password": "@password123PP", "full_name": "Chaminda Silva",           "role": UserRole.STAFF,  "phone": "070-1020-002", "photo_url": avatar("Chaminda")},
        {"email": "admin1@vetra.com", "password": "@password123PP", "full_name": "Sahan De Silva",          "role": UserRole.ADMIN,  "phone": "070-1000-001", "photo_url": avatar("Sahan")},
    ]
    users = []
    for u in users_data:
        user = User(
            email=u["email"],
            password_hash=hashpw(u["password"]),
            full_name=u["full_name"],
            role=u["role"],
            phone=u["phone"],
            photo_url=u["photo_url"],
        )
        users.append(user)
    session.add_all(users)
    await session.flush()
    print(f"  ✓ {len(users)} users")

    vet1, vet2, vet3 = users[0], users[1], users[2]
    staff1, staff2 = users[3], users[4]

    # ── Owners ─────────────────────────────
    owners_data = [
        {"first_name": "Anuradha",     "last_name": "Perera",        "email": "anuradha@example.com",      "phone": "94707393930", "address": "45 Flower Rd, Colombo 07"},
        {"first_name": "Nuwan",        "last_name": "Fernando",      "email": "nuwan@example.com",         "phone": "94707393930", "address": "12 Galle Rd, Colombo 03"},
        {"first_name": "Dilini",       "last_name": "Jayasuriya",    "email": "dilini@example.com",        "phone": "94707393930", "address": "88 Temple Rd, Kandy"},
        {"first_name": "Sanjaya",      "last_name": "Gunasekara",    "email": "sanjaya@example.com",       "phone": "94707393930", "address": "23 Marine Drive, Colombo 06"},
        {"first_name": "Chathurika",   "last_name": "Wickramasinghe","email": "chathurika@example.com",    "phone": "94707393930", "address": "150 Peradeniya Rd, Kandy"},
        {"first_name": "Tharindu",     "last_name": "Rathnayake",    "email": "tharindu@example.com",      "phone": "94707393930", "address": "9 Hill St, Nuwara Eliya"},
        {"first_name": "Nadeeja",      "last_name": "Jayawardena",   "email": "nadeeja@example.com",       "phone": "94707393930", "address": "34 Hospital Rd, Galle"},
        {"first_name": "Asanka",       "last_name": "Weerasinghe",   "email": "asanka@example.com",        "phone": "94707393930", "address": "7 Lake Rd, Anuradhapura"},
    ]
    owners = [Owner(**o) for o in owners_data]
    session.add_all(owners)
    await session.flush()
    print(f"  ✓ {len(owners)} owners")

    # ── Pets ───────────────────────────────
    pets_data = [
        {"owner_id": owners[0].id, "name": "Max",       "species": PetSpecies.DOG,     "breed": "Golden Retriever",  "gender": PetGender.MALE,   "date_of_birth": date(2020, 3, 15),  "weight_kg": 32.5, "color": "Golden",     "microchip_id": "MC-10001"},
        {"owner_id": owners[0].id, "name": "Luna",      "species": PetSpecies.CAT,     "breed": "Siamese",          "gender": PetGender.FEMALE, "date_of_birth": date(2021, 7, 22),  "weight_kg": 4.2,  "color": "Cream",      "microchip_id": "MC-10002"},
        {"owner_id": owners[1].id, "name": "Cooper",    "species": PetSpecies.DOG,     "breed": "Labrador Retriever","gender": PetGender.MALE,   "date_of_birth": date(2019, 11, 5),  "weight_kg": 28.0, "color": "Chocolate",  "microchip_id": "MC-10003"},
        {"owner_id": owners[2].id, "name": "Bella",     "species": PetSpecies.CAT,     "breed": "Siamese",           "gender": PetGender.FEMALE, "date_of_birth": date(2021, 5, 18),  "weight_kg": 12.8, "color": "Tricolor",   "microchip_id": "MC-10005"},
        {"owner_id": owners[2].id, "name": "Rocky",     "species": PetSpecies.DOG,  "breed": "Holland Lop",      "gender": PetGender.MALE,   "date_of_birth": date(2023, 2, 28),  "weight_kg": 1.8,  "color": "White",      "microchip_id": None},
        {"owner_id": owners[3].id, "name": "Daisy",     "species": PetSpecies.DOG,     "breed": "Cocker Spaniel",   "gender": PetGender.FEMALE, "date_of_birth": date(2020, 9, 3),   "weight_kg": 14.2, "color": "Golden",     "microchip_id": "MC-10006"},
        {"owner_id": owners[3].id, "name": "Milo",      "species": PetSpecies.CAT,     "breed": "Persian",          "gender": PetGender.MALE,   "date_of_birth": date(2022, 6, 14),  "weight_kg": 5.0,  "color": "White",      "microchip_id": "MC-10007"},
        {"owner_id": owners[4].id, "name": "Buddy",     "species": PetSpecies.DOG,     "breed": "German Shepherd",  "gender": PetGender.MALE,   "date_of_birth": date(2018, 4, 20),  "weight_kg": 35.0, "color": "Black & Tan", "microchip_id": "MC-10008"},
        {"owner_id": owners[4].id, "name": "Coco",      "species": PetSpecies.CAT,    "breed": "Persian",        "gender": PetGender.FEMALE, "date_of_birth": date(2023, 8, 1),   "weight_kg": 0.09, "color": "Grey",       "microchip_id": None},
        {"owner_id": owners[5].id, "name": "Bailey",    "species": PetSpecies.DOG,     "breed": "Poodle",           "gender": PetGender.FEMALE, "date_of_birth": date(2021, 12, 12), "weight_kg": 8.5,  "color": "White",      "microchip_id": "MC-10009"},
        {"owner_id": owners[5].id, "name": "Oliver",    "species": PetSpecies.CAT,     "breed": "Bengal",           "gender": PetGender.MALE,   "date_of_birth": date(2022, 10, 5),  "weight_kg": 5.5,  "color": "Spotted",    "microchip_id": "MC-10010"},
        {"owner_id": owners[6].id, "name": "Lily",      "species": PetSpecies.DOG,     "breed": "Shih Tzu",         "gender": PetGender.FEMALE, "date_of_birth": date(2023, 3, 8),   "weight_kg": 6.2,  "color": "Brown",      "microchip_id": "MC-10011"},
        {"owner_id": owners[6].id, "name": "Zoe",       "species": PetSpecies.CAT,     "breed": "Ragdoll",          "gender": PetGender.FEMALE, "date_of_birth": date(2021, 8, 30),  "weight_kg": 4.8,  "color": "Seal Point",  "microchip_id": "MC-10012"},
        {"owner_id": owners[7].id, "name": "Tucker",    "species": PetSpecies.DOG,     "breed": "Australian Shepherd","gender": PetGender.MALE,  "date_of_birth": date(2020, 6, 25),  "weight_kg": 22.0, "color": "Blue Merle",  "microchip_id": "MC-10013"},
        {"owner_id": owners[7].id, "name": "Pepper",    "species": PetSpecies.CAT,     "breed": "Calico",           "gender": PetGender.FEMALE, "date_of_birth": date(2022, 4, 17),  "weight_kg": 4.0,  "color": "Calico",     "microchip_id": "MC-10014"},
    ]

    pet_photos = {
        PetSpecies.DOG: f"{settings.PUBLIC_BASE_URL.rstrip('/')}/static/pets/dog-svgrepo-com.svg",
        PetSpecies.CAT: f"{settings.PUBLIC_BASE_URL.rstrip('/')}/static/pets/cat-svgrepo-com.svg",
    }

    pets = [
        Pet(**p, photo_url=pet_photos.get(p["species"]))
        for p in pets_data
    ]

    session.add_all(pets)
    await session.flush()
    print(f"  ✓ {len(pets)} pets")

    # ── Appointments ───────────────────────
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    now_hour = datetime.now(timezone.utc).hour

    appointments_data = [
        # Today's appointments
        {"pet_id": pets[0].id,  "vet_id": vet1.id, "owner_id": owners[0].id, "room_id": rooms[0].id, "start_time": today.replace(hour=9,  minute=0),  "end_time": today.replace(hour=9,  minute=30), "status": AppointmentStatus.SCHEDULED,    "reason": "Annual wellness exam",           "is_urgent": False},
        {"pet_id": pets[2].id,  "vet_id": vet1.id, "owner_id": owners[1].id, "room_id": rooms[1].id, "start_time": today.replace(hour=10, minute=0),  "end_time": today.replace(hour=10, minute=30), "status": AppointmentStatus.SCHEDULED,   "reason": "Severe itching — suspected atopic dermatitis", "is_urgent": False},
        {"pet_id": pets[4].id,  "vet_id": vet2.id, "owner_id": owners[2].id, "room_id": rooms[2].id, "start_time": today.replace(hour=10, minute=0),  "end_time": today.replace(hour=10, minute=30), "status": AppointmentStatus.SCHEDULED,   "reason": "Limping — possible sprain",     "is_urgent": False},
        {"pet_id": pets[8].id,  "vet_id": vet2.id, "owner_id": owners[4].id, "room_id": rooms[0].id, "start_time": today.replace(hour=10, minute=30), "end_time": today.replace(hour=11, minute=0),  "status": AppointmentStatus.SCHEDULED,     "reason": "Dental cleaning",                "is_urgent": False},
        {"pet_id": pets[10].id, "vet_id": vet1.id, "owner_id": owners[5].id, "room_id": rooms[1].id, "start_time": today.replace(hour=11, minute=0),  "end_time": today.replace(hour=11, minute=30), "status": AppointmentStatus.SCHEDULED,   "reason": "Skin rash examination",          "is_urgent": False},
        {"pet_id": pets[12].id, "vet_id": vet3.id, "owner_id": owners[6].id, "room_id": rooms[3].id, "start_time": today.replace(hour=11, minute=30), "end_time": today.replace(hour=12, minute=30), "status": AppointmentStatus.SCHEDULED,     "reason": "Surgery — spay",                "is_urgent": False},
        {"pet_id": pets[14].id, "vet_id": vet3.id, "owner_id": owners[7].id, "room_id": rooms[0].id, "start_time": today.replace(hour=13, minute=0),  "end_time": today.replace(hour=13, minute=30), "status": AppointmentStatus.SCHEDULED,     "reason": "Urgent — vomiting since yesterday","is_urgent": True},
        {"pet_id": pets[6].id,  "vet_id": vet1.id, "owner_id": owners[3].id, "room_id": rooms[2].id, "start_time": today.replace(hour=14, minute=0),  "end_time": today.replace(hour=14, minute=30), "status": AppointmentStatus.SCHEDULED,     "reason": "Follow-up ear infection",        "is_urgent": False},
        {"pet_id": pets[1].id,  "vet_id": vet2.id, "owner_id": owners[0].id, "room_id": rooms[1].id, "start_time": today.replace(hour=14, minute=30), "end_time": today.replace(hour=15, minute=0),  "status": AppointmentStatus.SCHEDULED,     "reason": "Urinary tract symptoms",         "is_urgent": True},
        # Past appointments
        {"pet_id": pets[0].id,  "vet_id": vet1.id, "owner_id": owners[0].id, "room_id": rooms[0].id, "start_time": today.replace(hour=0, minute=0) - timedelta(days=30, hours=9),  "end_time": today.replace(hour=0, minute=0) - timedelta(days=30, hours=9, minutes=-30), "status": AppointmentStatus.SCHEDULED, "reason": "Annual checkup", "is_urgent": False},
        {"pet_id": pets[4].id,  "vet_id": vet2.id, "owner_id": owners[2].id, "room_id": rooms[1].id, "start_time": today.replace(hour=0, minute=0) - timedelta(days=14, hours=10), "end_time": today.replace(hour=0, minute=0) - timedelta(days=14, hours=10, minutes=-30), "status": AppointmentStatus.SCHEDULED, "reason": "Allergy consult", "is_urgent": False},
        {"pet_id": pets[8].id,  "vet_id": vet1.id, "owner_id": owners[4].id, "room_id": rooms[2].id, "start_time": today.replace(hour=0, minute=0) - timedelta(days=7, hours=11),  "end_time": today.replace(hour=0, minute=0) - timedelta(days=7, hours=11, minutes=-30),  "status": AppointmentStatus.SCHEDULED, "reason": "Vaccination", "is_urgent": False},
        {"pet_id": pets[14].id, "vet_id": vet3.id, "owner_id": owners[7].id, "room_id": rooms[0].id, "start_time": today.replace(hour=0, minute=0) - timedelta(days=3, hours=15),   "end_time": today.replace(hour=0, minute=0) - timedelta(days=3, hours=15, minutes=-30),   "status": AppointmentStatus.SCHEDULED, "reason": "Eye infection", "is_urgent": False},
        # Future appointments
        {"pet_id": pets[3].id,  "vet_id": vet1.id, "owner_id": owners[2].id, "room_id": rooms[0].id, "start_time": today.replace(hour=0, minute=0) + timedelta(days=1, hours=9),   "end_time": today.replace(hour=0, minute=0) + timedelta(days=1, hours=9, minutes=30),   "status": AppointmentStatus.SCHEDULED,  "reason": "wellness exam", "is_urgent": False},
        {"pet_id": pets[6].id,  "vet_id": vet2.id, "owner_id": owners[3].id, "room_id": rooms[1].id, "start_time": today.replace(hour=0, minute=0) + timedelta(days=2, hours=10),   "end_time": today.replace(hour=0, minute=0) + timedelta(days=2, hours=10, minutes=30),   "status": AppointmentStatus.SCHEDULED,  "reason": "grooming + nail trim", "is_urgent": False},
    ]
    appointments = [Appointment(**a) for a in appointments_data]
    session.add_all(appointments)
    await session.flush()
    print(f"  ✓ {len(appointments)} appointments")

    # ── Medical Records ────────────────────
    med_records_data = [
        {"pet_id": pets[0].id, "vet_id": vet1.id, "appointment_id": appointments[9].id,
         "record_type": RecordType.EXAMINATION, "diagnosis": "Healthy — no issues found", "treatment": "Routine vaccination administered", "recorded_at": dt(-30)},
        {"pet_id": pets[0].id, "vet_id": vet1.id, "appointment_id": appointments[0].id,
         "record_type": RecordType.VACCINATION, "diagnosis": "Due for DAPP booster", "treatment": "DAPP vaccine administered, 1ml IM", "recorded_at": dt(0)},
        {"pet_id": pets[4].id, "vet_id": vet2.id, "appointment_id": appointments[10].id,
         "record_type": RecordType.EXAMINATION, "diagnosis": "Seasonal environmental allergies", "treatment": "Prescribed Apoquel 5.4mg BID for 14 days", "recorded_at": dt(-14)},
        {"pet_id": pets[8].id, "vet_id": vet1.id, "appointment_id": appointments[11].id,
         "record_type": RecordType.VACCINATION, "diagnosis": "Rabies booster due", "treatment": "Rabies vaccine administered SQ", "recorded_at": dt(-7)},
        {"pet_id": pets[14].id, "vet_id": vet3.id, "appointment_id": appointments[12].id,
         "record_type": RecordType.EXAMINATION, "diagnosis": "Conjunctivitis — left eye", "treatment": "Terramycin ophthalmic ointment BID x 7 days", "recorded_at": dt(-3)},
        {"pet_id": pets[6].id, "vet_id": vet1.id, "appointment_id": None,
         "record_type": RecordType.SURGERY, "diagnosis": "Grade II patellar luxation", "treatment": "Surgical correction performed under general anesthesia", "recorded_at": dt(-60)},
        {"pet_id": pets[2].id, "vet_id": vet1.id, "appointment_id": None,
         "record_type": RecordType.DENTAL, "diagnosis": "Periodontal disease — Stage II", "treatment": "Dental scaling and polishing, extracted #204", "recorded_at": dt(-45)},
        {"pet_id": pets[2].id, "vet_id": vet1.id, "appointment_id": None,
         "record_type": RecordType.EXAMINATION, "diagnosis": "Canine atopic dermatitis — pruritus flare", "treatment": "Started Meloxicam 1.5mg SID for concurrent joint discomfort; continued antihistamine therapy", "recorded_at": dt(-20)},
    ]
    med_records = [MedicalRecord(**r) for r in med_records_data]
    session.add_all(med_records)
    await session.flush()
    print(f"  ✓ {len(med_records)} medical records")

    # ── Vaccinations ───────────────────────
    vaccinations_data = [
        {"pet_id": pets[0].id, "vaccine_name": "DAPP", "vaccine_type": "Core", "administered_date": date.today() - timedelta(days=30), "next_due_date": date.today() + timedelta(days=335), "vet_id": vet1.id, "batch_number": "BATCH-2024-001"},
        {"pet_id": pets[0].id, "vaccine_name": "Rabies", "vaccine_type": "Core", "administered_date": date.today(), "next_due_date": date.today() + timedelta(days=365), "vet_id": vet1.id, "batch_number": "BATCH-2024-002"},
        {"pet_id": pets[4].id, "vaccine_name": "DAPP", "vaccine_type": "Core", "administered_date": date.today() - timedelta(days=180), "next_due_date": date.today() + timedelta(days=185), "vet_id": vet2.id, "batch_number": "BATCH-2024-001"},
        {"pet_id": pets[4].id, "vaccine_name": "Bordetella", "vaccine_type": "Non-Core", "administered_date": date.today() - timedelta(days=180), "next_due_date": date.today() + timedelta(days=185), "vet_id": vet2.id, "batch_number": "BATCH-2024-003"},
        {"pet_id": pets[8].id, "vaccine_name": "Rabies", "vaccine_type": "Core", "administered_date": date.today() - timedelta(days=7), "next_due_date": date.today() + timedelta(days=358), "vet_id": vet1.id, "batch_number": "BATCH-2024-002"},
    ]
    vaccinations = [Vaccination(**v) for v in vaccinations_data]
    session.add_all(vaccinations)
    await session.flush()
    print(f"  ✓ {len(vaccinations)} vaccinations")

    # ── Lab Results ────────────────────────
    lab_results_data = [
        {"pet_id": pets[1].id, "appointment_id": None, "test_name": "Complete Blood Count", "test_category": "Hematology",
         "result_value": "WBC: 12.5, RBC: 7.2", "reference_range": "WBC: 5.5-19.5, RBC: 5.0-10.0", "unit": "x10^9/L",
         "is_abnormal": False, "performed_by": vet1.id, "result_date": dt(-2)},
        {"pet_id": pets[1].id, "appointment_id": None, "test_name": "Urinalysis", "test_category": "Urine",
         "result_value": "pH: 8.5, Protein: 2+", "reference_range": "pH: 6.0-7.5", "unit": "",
         "is_abnormal": True, "performed_by": vet1.id, "result_date": dt(-2), "notes": "Elevated pH and protein suggest possible UTI"},
        {"pet_id": pets[4].id, "appointment_id": None, "test_name": "Allergy Panel", "test_category": "Immunology",
         "result_value": "Positive: dust mites, grass pollen", "reference_range": "Negative", "unit": "",
         "is_abnormal": True, "performed_by": vet2.id, "result_date": dt(-14)},
        {"pet_id": pets[14].id, "appointment_id": None, "test_name": "Eye Swab Culture", "test_category": "Microbiology",
         "result_value": "Staphylococcus intermedius isolated", "reference_range": "No growth", "unit": "",
         "is_abnormal": True, "performed_by": vet3.id, "result_date": dt(-3)},
    ]
    lab_results = [LabResult(**l) for l in lab_results_data]
    session.add_all(lab_results)
    await session.flush()
    print(f"  ✓ {len(lab_results)} lab results")

    # ── Clinical Notes ─────────────────────
    clinical_notes_data = [
        {"pet_id": pets[0].id, "appointment_id": appointments[0].id, "vet_id": vet1.id,
         "raw_transcript": "Max is a 5-year-old male Golden Retriever here for annual wellness exam. Owner reports he's been eating well and active. No concerns. Physical exam: temperature 101.2F, heart rate 80, respiratory rate 20. Eyes clear, ears clean, teeth show mild tartar. Heart and lungs auscultated normal. Abdomen soft. Recommended dental cleaning. Vaccinations updated. Overall healthy.",
         "status": ClinicalNoteStatus.COMPLETED, "ai_model_version": "vetra-ai-v1"},
        {"pet_id": pets[4].id, "appointment_id": appointments[2].id, "vet_id": vet2.id,
         "raw_transcript": "Bella presenting with acute lameness on right forelimb. Owner noticed yesterday after running in the park. Physical exam: weight-bearing lameness, mild swelling over carpus. Palpation elicits pain response. Range of motion slightly reduced. Suspect carpal sprain. Prescribed rest and NSAIDs for 5 days. Recheck if not improved.",
         "status": ClinicalNoteStatus.PENDING, "ai_model_version": None},
        {"pet_id": pets[14].id, "appointment_id": appointments[6].id, "vet_id": vet3.id,
         "raw_transcript": "Tucker presented as emergency — vomiting and lethargy since yesterday. Owner reports possible ingestion of table scraps. Physical exam: dehydrated, abdominal pain on palpation. Temperature 102.8F. Blood work shows elevated liver enzymes. Started IV fluids and antiemetics. Will monitor overnight.",
         "status": ClinicalNoteStatus.DRAFT, "ai_model_version": None},
    ]
    clinical_notes = [ClinicalNote(**c) for c in clinical_notes_data]
    session.add_all(clinical_notes)
    await session.flush()
    print(f"  ✓ {len(clinical_notes)} clinical notes")

    # ── Prescriptions ──────────────────────
    prescriptions_data = [
        {"clinical_note_id": clinical_notes[1].id, "pet_id": pets[4].id, "vet_id": vet2.id,
         "medication_name": "Carprofen", "dosage": "50mg", "frequency": "BID", "duration": "5 days", "route": "Oral", "notes": "Give with food"},
        {"clinical_note_id": None, "pet_id": pets[1].id, "vet_id": vet1.id,
         "medication_name": "Amoxicillin", "dosage": "50mg", "frequency": "BID", "duration": "10 days", "route": "Oral", "notes": "Suspected UTI"},
        {"clinical_note_id": None, "pet_id": pets[14].id, "vet_id": vet3.id,
         "medication_name": "Maropitant", "dosage": "16mg", "frequency": "SID", "duration": "3 days", "route": "IV", "notes": "Antiemetic"},
        {"clinical_note_id": None, "pet_id": pets[2].id, "vet_id": vet1.id,
         "medication_name": "Meloxicam", "dosage": "1.5mg", "frequency": "SID", "duration": "ongoing", "route": "Oral", "notes": "Current medication — verify NSAID compatibility before adding new drugs"},
    ]
    prescriptions = [Prescription(**p) for p in prescriptions_data]
    session.add_all(prescriptions)
    await session.flush()
    print(f"  ✓ {len(prescriptions)} prescriptions")

    # ── Inventory (prices in LKR) ────────────
    inventory_data = [
        {"name": "Rabies Vaccine",           "category": InventoryCategory.VACCINE,   "unit": "dose",   "quantity": 25,  "min_quantity": 10,  "price_per_unit": 800.00, "supplier": "Zoetis",              "batch_number": "RB-2024-01", "expiry_date": date(2025, 6, 1)},
        {"name": "DAPP Vaccine",             "category": InventoryCategory.VACCINE,   "unit": "dose",   "quantity": 18,  "min_quantity": 10,  "price_per_unit": 900.00, "supplier": "Merck Animal Health", "batch_number": "DP-2024-02", "expiry_date": date(2025, 7, 1)},
        {"name": "Carprofen 50mg",           "category": InventoryCategory.MEDICATION,"unit": "tablet", "quantity": 120, "min_quantity": 30,  "price_per_unit": 40.00,  "supplier": "Zoetis",              "batch_number": "CP-2024-01", "expiry_date": date(2026, 1, 1)},
        {"name": "Amoxicillin 250mg",        "category": InventoryCategory.MEDICATION,"unit": "tablet", "quantity": 100, "min_quantity": 30,  "price_per_unit": 25.00,  "supplier": "Sandoz",               "batch_number": "AX-2024-01", "expiry_date": date(2025, 12, 1)},
        {"name": "Meloxicam 1.5mg",         "category": InventoryCategory.MEDICATION,"unit": "tablet", "quantity": 5,   "min_quantity": 20,  "price_per_unit": 30.00,  "supplier": "Boehringer Ingelheim", "batch_number": "MX-2024-01", "expiry_date": date(2025, 9, 1)},
        {"name": "Maropitant 16mg",          "category": InventoryCategory.MEDICATION,"unit": "tablet", "quantity": 8,   "min_quantity": 15,  "price_per_unit": 150.00, "supplier": "Zoetis",              "batch_number": "MP-2024-01", "expiry_date": date(2025, 5, 1)},
        {"name": "Fluid — LRS 1L",           "category": InventoryCategory.SUPPLY,    "unit": "bag",    "quantity": 14,  "min_quantity": 10,  "price_per_unit": 500.00, "supplier": "Baxter",               "batch_number": "LRS-2024-01", "expiry_date": date(2025, 8, 1)},
        {"name": "Surgical Gloves (Size 7)", "category": InventoryCategory.SUPPLY,    "unit": "pair",   "quantity": 50,  "min_quantity": 40,  "price_per_unit": 60.00,  "supplier": "Medline",              "batch_number": None,          "expiry_date": None},
        {"name": "Syringes 3ml",             "category": InventoryCategory.SUPPLY,    "unit": "each",   "quantity": 300, "min_quantity": 100, "price_per_unit": 15.00,  "supplier": "BD",                   "batch_number": None,          "expiry_date": None},
        {"name": "Prescription Diet — Renal","category": InventoryCategory.FOOD,      "unit": "bag",    "quantity": 4,   "min_quantity": 5,   "price_per_unit": 1800.00,"supplier": "Hill's Pet Nutrition","batch_number": "RD-2024-01",  "expiry_date": date(2025, 4, 1)},
        {"name": "Royal Canin Gastro",       "category": InventoryCategory.FOOD,      "unit": "bag",    "quantity": 7,   "min_quantity": 5,   "price_per_unit": 1600.00,"supplier": "Royal Canin",          "batch_number": "GI-2024-01",  "expiry_date": date(2025, 3, 1)},
        {"name": "Ultrasound Gel",           "category": InventoryCategory.SUPPLY,    "unit": "bottle", "quantity": 3,   "min_quantity": 5,   "price_per_unit": 650.00, "supplier": "Parker Labs",          "batch_number": None,          "expiry_date": None},
        {"name": "Flea & Tick Prevention",   "category": InventoryCategory.MEDICATION,"unit": "dose",   "quantity": 22,  "min_quantity": 15,  "price_per_unit": 700.00, "supplier": "Bayer",                "batch_number": "FT-2024-01",  "expiry_date": date(2025, 10, 1)},
        {"name": "Heartworm Prevention",      "category": InventoryCategory.MEDICATION,"unit": "dose",   "quantity": 18,  "min_quantity": 15,  "price_per_unit": 900.00, "supplier": "Merck Animal Health", "batch_number": "HW-2024-01",  "expiry_date": date(2025, 11, 1)},
    ]
    inventory_items = [Inventory(**i) for i in inventory_data]
    session.add_all(inventory_items)
    await session.flush()
    print(f"  ✓ {len(inventory_items)} inventory items")

    # ── Invoices (LKR) ──────────────────────
    # invoices_data = [
    #     {"appointment_id": appointments[9].id,  "owner_id": owners[0].id, "pet_id": pets[0].id,  "total_amount": 1800.00, "paid_amount": 1800.00, "status": InvoiceStatus.PAID,        "payment_method": PaymentMethod.CREDIT_CARD, "paid_at": dt(-30)},
    #     {"appointment_id": appointments[10].id, "owner_id": owners[2].id, "pet_id": pets[4].id,  "total_amount": 3700.00, "paid_amount": 3700.00, "status": InvoiceStatus.PAID,        "payment_method": PaymentMethod.CASH,         "paid_at": dt(-14)},
    #     {"appointment_id": appointments[11].id, "owner_id": owners[4].id, "pet_id": pets[8].id,  "total_amount": 1300.00, "paid_amount": 1300.00, "status": InvoiceStatus.PAID,        "payment_method": PaymentMethod.DEBIT_CARD,   "paid_at": dt(-7)},
    # ]
    # invoices = [Invoice(**i) for i in invoices_data]
    # session.add_all(invoices)
    # await session.flush()
    # print(f"  ✓ {len(invoices)} invoices")

    # # ── Invoice Items ──────────────────────
    # invoice_items_data = [
    #     {"invoice_id": invoices[0].id, "description": "Annual Wellness Exam",                    "quantity": 1, "unit_price": 500.00, "total_price": 500.00},
    #     {"invoice_id": invoices[0].id, "description": "DAPP Vaccine",                            "quantity": 1, "unit_price": 900.00, "total_price": 900.00},
    #     {"invoice_id": invoices[0].id, "description": "Office Visit Fee",                        "quantity": 1, "unit_price": 400.00, "total_price": 400.00},
    #     {"invoice_id": invoices[1].id, "description": "Allergy Consultation",                    "quantity": 1, "unit_price": 2200.00, "total_price": 2200.00},
    #     {"invoice_id": invoices[1].id, "description": "Apoquel 5.4mg (14 tablets)",             "quantity": 1, "unit_price": 1200.00, "total_price": 1200.00},
    #     {"invoice_id": invoices[1].id, "description": "Office Visit Fee",                        "quantity": 1, "unit_price": 300.00, "total_price": 300.00},
    #     {"invoice_id": invoices[2].id, "description": "Rabies Vaccination",                      "quantity": 1, "unit_price": 800.00, "total_price": 800.00},
    #     {"invoice_id": invoices[2].id, "description": "Office Visit Fee",                        "quantity": 1, "unit_price": 500.00, "total_price": 500.00},
    # ]
    # invoice_items = [InvoiceItem(**i) for i in invoice_items_data]
    # session.add_all(invoice_items)
    # await session.flush()
    # print(f"  ✓ {len(invoice_items)} invoice items")

    # ── Weight Records ─────────────────────
    weight_records_data = [
        {"pet_id": pets[0].id, "weight_kg": 32.5, "recorded_by": vet1.id, "recorded_at": dt(-30)},
        {"pet_id": pets[0].id, "weight_kg": 31.8, "recorded_by": vet1.id, "recorded_at": dt(-180)},
        {"pet_id": pets[0].id, "weight_kg": 30.2, "recorded_by": vet1.id, "recorded_at": dt(-365)},
        {"pet_id": pets[4].id, "weight_kg": 12.8, "recorded_by": vet2.id, "recorded_at": dt(-14)},
        {"pet_id": pets[4].id, "weight_kg": 13.1, "recorded_by": vet2.id, "recorded_at": dt(-180)},
        {"pet_id": pets[4].id, "weight_kg": 12.5, "recorded_by": vet2.id, "recorded_at": dt(-365)},
        {"pet_id": pets[2].id, "weight_kg": 28.4, "recorded_by": vet1.id, "recorded_at": dt(-20)},
        {"pet_id": pets[2].id, "weight_kg": 29.1, "recorded_by": vet1.id, "recorded_at": dt(-120)},
        {"pet_id": pets[2].id, "weight_kg": 27.6, "recorded_by": vet1.id, "recorded_at": dt(-250)},
    ]
    weight_records = [WeightRecord(**w) for w in weight_records_data]
    session.add_all(weight_records)
    await session.flush()
    print(f"  ✓ {len(weight_records)} weight records")

    # ── Summary ────────────────────────────
    print()
    print("=" * 48)
    print("  🌿 Database seeded successfully!")
    print("=" * 48)
    print()
    print("  Login credentials:")
    print("  ─────────────────────────────────")
    print(f"  Vet:   vet1@vetra.com   / password123")
    print(f"  Vet:   vet2@vetra.com  / password123")
    print(f"  Vet:   vet3@vetra.com  / password123")
    print(f"  Staff: staff1@vetra.com / password123")
    print(f"  Staff: staff2@vetra.com / password123")
    print(f"  Admin: admin1@vetra.com / password123")
    print()
    print(f"  Today's appointments: {sum(1 for a in appointments_data if a['start_time'].date() == today.date())}")
    print(f"  Low-stock items: {sum(1 for i in inventory_data if i['quantity'] < i['min_quantity'])}")
    # print(f"  Pending invoices: {sum(1 for i in invoices_data if i['status'] == InvoiceStatus.PENDING)}")
    print()


async def main():
    async with AsyncSession(engine) as session:
        await seed(session)
        await session.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
