import enum


class UserRole(str, enum.Enum):
    VET = "vet"
    STAFF = "staff"
    ADMIN = "admin"


class PetSpecies(str, enum.Enum):
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    RABBIT = "rabbit"
    REPTILE = "reptile"
    HORSE = "horse"
    FERRET = "ferret"
    OTHER = "other"


class PetGender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class RecordType(str, enum.Enum):
    EXAMINATION = "examination"
    VACCINATION = "vaccination"
    SURGERY = "surgery"
    DENTAL = "dental"
    LAB_WORK = "lab_work"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    OTHER = "other"


class ClinicalNoteStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEWED = "reviewed"


class InventoryCategory(str, enum.Enum):
    MEDICATION = "medication"
    VACCINE = "vaccine"
    SUPPLY = "supply"
    FOOD = "food"
    EQUIPMENT = "equipment"


class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    INSURANCE = "insurance"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"
