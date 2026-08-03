import type {
  User, Owner, Pet, Appointment, MedicalRecord, ClinicalNote,
  InventoryItem, Invoice, InvoiceItem, VetDashboard, StaffDashboard,
} from './api'

export function isDemo(): boolean {
  if (typeof window === 'undefined') return false
  return new URLSearchParams(window.location.search).get('demo') === '1'
}

export function sleep(ms: number): Promise<void> {
  return new Promise((res) => setTimeout(res, ms))
}

export function demoId(prefix: string, n: number): string {
  return `${prefix}_${String(n).padStart(3, '0')}`
}

// ── Time helpers (dynamic "today" so the demo always looks live) ──
function at(hour: number, min: number): Date {
  const d = new Date()
  d.setHours(hour, min, 0, 0)
  return d
}

function fmt(d: Date): string {
  return d.toISOString()
}

// ── Scripted dataset (mirrors backend/scripts/seed.py) ──

const demoUser: User = {
  id: 'usr_staff1', email: 'staff1@vetra.com', full_name: 'Jessica Rodriguez',
  role: 'staff', phone: '555-0201', is_active: true, created_at: fmt(new Date()),
}

const demoVetUser: User = {
  id: 'usr_vet1', email: 'vet1@vetra.com', full_name: 'Dr. Sarah Chen',
  role: 'vet', phone: '555-0101', is_active: true, created_at: fmt(new Date()),
}

const owners: Owner[] = [
  { id: 'own_alice', first_name: 'Alice', last_name: 'Thompson', email: 'alice@example.com', phone: '555-1001', address: '123 Oak St, Portland, OR', notes: null, is_active: true, created_at: fmt(at(8, 0)), updated_at: fmt(at(8, 0)) },
  { id: 'own_bob', first_name: 'Bob', last_name: 'Martinez', email: 'bob@example.com', phone: '555-1002', address: '456 Pine Ave, Portland, OR', notes: null, is_active: true, created_at: fmt(at(8, 0)), updated_at: fmt(at(8, 0)) },
  { id: 'own_carol', first_name: 'Carol', last_name: 'Williams', email: 'carol@example.com', phone: '555-1003', address: '789 Elm Dr, Portland, OR', notes: null, is_active: true, created_at: fmt(at(8, 0)), updated_at: fmt(at(8, 0)) },
  { id: 'own_emma', first_name: 'Emma', last_name: 'Davis', email: 'emma@example.com', phone: '555-1005', address: '654 Cedar St, Portland, OR', notes: null, is_active: true, created_at: fmt(at(8, 0)), updated_at: fmt(at(8, 0)) },
  { id: 'own_henry', first_name: 'Henry', last_name: 'Wilson', email: 'henry@example.com', phone: '555-1008', address: '753 Spruce Ct, Portland, OR', notes: null, is_active: true, created_at: fmt(at(8, 0)), updated_at: fmt(at(8, 0)) },
]

const pets: Pet[] = [
  { id: 'pet_max', owner_id: 'own_alice', name: 'Max', species: 'dog', breed: 'Golden Retriever', color: 'Golden', gender: 'male', date_of_birth: '2020-03-15', weight_kg: 32.5, microchip_id: 'MC-10001', photo_url: null, is_active: true, created_at: fmt(at(8, 0)), updated_at: fmt(at(8, 0)) },
  { id: 'pet_cooper', owner_id: 'own_bob', name: 'Cooper', species: 'dog', breed: 'Labrador Retriever', color: 'Chocolate', gender: 'male', date_of_birth: '2019-11-05', weight_kg: 28.0, microchip_id: 'MC-10003', photo_url: null, is_active: true, created_at: fmt(at(8, 0)), updated_at: fmt(at(8, 0)) },
  { id: 'pet_bella', owner_id: 'own_carol', name: 'Bella', species: 'dog', breed: 'Beagle', color: 'Tricolor', gender: 'female', date_of_birth: '2021-05-18', weight_kg: 12.8, microchip_id: 'MC-10005', photo_url: null, is_active: true, created_at: fmt(at(8, 0)), updated_at: fmt(at(8, 0)) },
  { id: 'pet_buddy', owner_id: 'own_emma', name: 'Buddy', species: 'dog', breed: 'German Shepherd', color: 'Black & Tan', gender: 'male', date_of_birth: '2018-04-20', weight_kg: 35.0, microchip_id: 'MC-10008', photo_url: null, is_active: true, created_at: fmt(at(8, 0)), updated_at: fmt(at(8, 0)) },
  { id: 'pet_tucker', owner_id: 'own_henry', name: 'Tucker', species: 'dog', breed: 'Australian Shepherd', color: 'Blue Merle', gender: 'male', date_of_birth: '2020-06-25', weight_kg: 22.0, microchip_id: 'MC-10013', photo_url: null, is_active: true, created_at: fmt(at(8, 0)), updated_at: fmt(at(8, 0)) },
]

const maxRecords: MedicalRecord[] = [
  { id: 'rec_max_01', pet_id: 'pet_max', vet_id: 'usr_vet1', appointment_id: null, record_type: 'examination', diagnosis: 'Healthy — no issues found', treatment: 'Routine vaccination administered', notes: null, recorded_at: fmt(at(9, 0)), created_at: fmt(at(9, 0)) },
]

let appointments: Appointment[] = [
  { id: 'apt_max', pet_id: 'pet_max', vet_id: 'usr_vet1', owner_id: 'own_alice', room_id: null, start_time: fmt(at(9, 0)), end_time: fmt(at(9, 30)), status: 'scheduled', reason: 'Annual wellness exam', notes: null, is_urgent: false, created_at: fmt(at(8, 30)), updated_at: fmt(at(8, 30)) },
  { id: 'apt_cooper', pet_id: 'pet_cooper', vet_id: 'usr_vet1', owner_id: 'own_bob', room_id: null, start_time: fmt(at(9, 30)), end_time: fmt(at(10, 0)), status: 'checked_in', reason: 'Vaccination booster', notes: null, is_urgent: false, created_at: fmt(at(8, 30)), updated_at: fmt(at(8, 30)) },
  { id: 'apt_bella', pet_id: 'pet_bella', vet_id: 'usr_vet1', owner_id: 'own_carol', room_id: null, start_time: fmt(at(10, 0)), end_time: fmt(at(10, 30)), status: 'in_progress', reason: 'Limping — possible sprain', notes: 'Owner noticed lameness yesterday.', is_urgent: false, created_at: fmt(at(8, 30)), updated_at: fmt(at(8, 30)) },
  { id: 'apt_buddy', pet_id: 'pet_buddy', vet_id: 'usr_vet1', owner_id: 'own_emma', room_id: null, start_time: fmt(at(10, 30)), end_time: fmt(at(11, 0)), status: 'scheduled', reason: 'Dental cleaning', notes: null, is_urgent: false, created_at: fmt(at(8, 30)), updated_at: fmt(at(8, 30)) },
  { id: 'apt_tucker', pet_id: 'pet_tucker', vet_id: 'usr_vet1', owner_id: 'own_henry', room_id: null, start_time: fmt(at(13, 0)), end_time: fmt(at(13, 30)), status: 'scheduled', reason: 'Urgent — vomiting since yesterday', notes: null, is_urgent: true, created_at: fmt(at(8, 30)), updated_at: fmt(at(8, 30)) },
]

let medicalRecords: MedicalRecord[] = [...maxRecords]

let inventory: InventoryItem[] = [
  { id: 'inv_rabies', name: 'Rabies Vaccine', category: 'vaccine', description: null, unit: 'dose', quantity: 25, min_quantity: 10, price_per_unit: 15.0, supplier: 'Zoetis', batch_number: 'RB-2024-01', expiry_date: '2025-06-01', is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
  { id: 'inv_dapp', name: 'DAPP Vaccine', category: 'vaccine', description: null, unit: 'dose', quantity: 18, min_quantity: 10, price_per_unit: 18.5, supplier: 'Merck Animal Health', batch_number: 'DP-2024-02', expiry_date: '2025-07-01', is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
  { id: 'inv_carprofen', name: 'Carprofen 50mg', category: 'medication', description: null, unit: 'tablet', quantity: 120, min_quantity: 30, price_per_unit: 0.75, supplier: 'Zoetis', batch_number: 'CP-2024-01', expiry_date: '2026-01-01', is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
  { id: 'inv_amoxicillin', name: 'Amoxicillin 250mg', category: 'medication', description: null, unit: 'tablet', quantity: 200, min_quantity: 50, price_per_unit: 0.45, supplier: 'Sandoz', batch_number: 'AX-2024-01', expiry_date: '2025-12-01', is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
  { id: 'inv_meloxicam', name: 'Meloxicam 1.5mg', category: 'medication', description: null, unit: 'tablet', quantity: 5, min_quantity: 20, price_per_unit: 0.6, supplier: 'Boehringer Ingelheim', batch_number: 'MX-2024-01', expiry_date: '2025-09-01', is_active: true, is_low_stock: true, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
  { id: 'inv_maropitant', name: 'Maropitant 16mg', category: 'medication', description: null, unit: 'tablet', quantity: 8, min_quantity: 15, price_per_unit: 2.5, supplier: 'Zoetis', batch_number: 'MP-2024-01', expiry_date: '2025-05-01', is_active: true, is_low_stock: true, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
  { id: 'inv_lrs', name: 'Fluid — LRS 1L', category: 'supply', description: null, unit: 'bag', quantity: 14, min_quantity: 10, price_per_unit: 4.0, supplier: 'Baxter', batch_number: 'LRS-2024-01', expiry_date: '2025-08-01', is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
  { id: 'inv_syringes', name: 'Syringes 3ml', category: 'supply', description: null, unit: 'each', quantity: 300, min_quantity: 100, price_per_unit: 0.12, supplier: 'BD', batch_number: null, expiry_date: null, is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
  { id: 'inv_gloves', name: 'Surgical Gloves (Size 7)', category: 'supply', description: null, unit: 'pair', quantity: 50, min_quantity: 40, price_per_unit: 0.35, supplier: 'Medline', batch_number: null, expiry_date: null, is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
  { id: 'inv_renal', name: 'Prescription Diet — Renal', category: 'food', description: null, unit: 'bag', quantity: 4, min_quantity: 5, price_per_unit: 22.5, supplier: 'Hill\'s Pet Nutrition', batch_number: 'RD-2024-01', expiry_date: '2025-04-01', is_active: true, is_low_stock: true, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
  { id: 'inv_usgel', name: 'Ultrasound Gel', category: 'supply', description: null, unit: 'bottle', quantity: 3, min_quantity: 5, price_per_unit: 8.0, supplier: 'Parker Labs', batch_number: null, expiry_date: null, is_active: true, is_low_stock: true, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
]

let invoices: Invoice[] = []
let invoiceItems: InvoiceItem[] = []

let clinicalNotes: ClinicalNote[] = []
let noteSeq = 0

let inventoryUpdateLog: string[] = []

export const demoState = {
  get demoUser() { return demoUser },
  get demoVetUser() { return demoVetUser },
  get appointments() { return appointments },
  get owners() { return owners },
  get pets() { return pets },
  get medicalRecords() { return medicalRecords },
  get inventory() { return inventory },
  get invoices() { return invoices },
  get invoiceItems() { return invoiceItems },
  get clinicalNotes() { return clinicalNotes },
  get inventoryUpdateLog() { return inventoryUpdateLog },
  set appointments(v) { appointments = v },
  set medicalRecords(v) { medicalRecords = v },
  set inventory(v) { inventory = v },
  set invoices(v) { invoices = v },
  set invoiceItems(v) { invoiceItems = v },
  nextNoteId() { return demoId('note', ++noteSeq) },
}

export function resetDemo() {
  appointments = [
    { id: 'apt_max', pet_id: 'pet_max', vet_id: 'usr_vet1', owner_id: 'own_alice', room_id: null, start_time: fmt(at(9, 0)), end_time: fmt(at(9, 30)), status: 'scheduled', reason: 'Annual wellness exam', notes: null, is_urgent: false, created_at: fmt(at(8, 30)), updated_at: fmt(at(8, 30)) },
    { id: 'apt_cooper', pet_id: 'pet_cooper', vet_id: 'usr_vet1', owner_id: 'own_bob', room_id: null, start_time: fmt(at(9, 30)), end_time: fmt(at(10, 0)), status: 'checked_in', reason: 'Vaccination booster', notes: null, is_urgent: false, created_at: fmt(at(8, 30)), updated_at: fmt(at(8, 30)) },
    { id: 'apt_bella', pet_id: 'pet_bella', vet_id: 'usr_vet1', owner_id: 'own_carol', room_id: null, start_time: fmt(at(10, 0)), end_time: fmt(at(10, 30)), status: 'in_progress', reason: 'Limping — possible sprain', notes: 'Owner noticed lameness yesterday.', is_urgent: false, created_at: fmt(at(8, 30)), updated_at: fmt(at(8, 30)) },
    { id: 'apt_buddy', pet_id: 'pet_buddy', vet_id: 'usr_vet1', owner_id: 'own_emma', room_id: null, start_time: fmt(at(10, 30)), end_time: fmt(at(11, 0)), status: 'scheduled', reason: 'Dental cleaning', notes: null, is_urgent: false, created_at: fmt(at(8, 30)), updated_at: fmt(at(8, 30)) },
    { id: 'apt_tucker', pet_id: 'pet_tucker', vet_id: 'usr_vet1', owner_id: 'own_henry', room_id: null, start_time: fmt(at(13, 0)), end_time: fmt(at(13, 30)), status: 'scheduled', reason: 'Urgent — vomiting since yesterday', notes: null, is_urgent: true, created_at: fmt(at(8, 30)), updated_at: fmt(at(8, 30)) },
  ]
  medicalRecords = [...maxRecords]
  inventory = [
    { id: 'inv_rabies', name: 'Rabies Vaccine', category: 'vaccine', description: null, unit: 'dose', quantity: 25, min_quantity: 10, price_per_unit: 15.0, supplier: 'Zoetis', batch_number: 'RB-2024-01', expiry_date: '2025-06-01', is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
    { id: 'inv_dapp', name: 'DAPP Vaccine', category: 'vaccine', description: null, unit: 'dose', quantity: 18, min_quantity: 10, price_per_unit: 18.5, supplier: 'Merck Animal Health', batch_number: 'DP-2024-02', expiry_date: '2025-07-01', is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
    { id: 'inv_carprofen', name: 'Carprofen 50mg', category: 'medication', description: null, unit: 'tablet', quantity: 120, min_quantity: 30, price_per_unit: 0.75, supplier: 'Zoetis', batch_number: 'CP-2024-01', expiry_date: '2026-01-01', is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
    { id: 'inv_amoxicillin', name: 'Amoxicillin 250mg', category: 'medication', description: null, unit: 'tablet', quantity: 200, min_quantity: 50, price_per_unit: 0.45, supplier: 'Sandoz', batch_number: 'AX-2024-01', expiry_date: '2025-12-01', is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
    { id: 'inv_meloxicam', name: 'Meloxicam 1.5mg', category: 'medication', description: null, unit: 'tablet', quantity: 5, min_quantity: 20, price_per_unit: 0.6, supplier: 'Boehringer Ingelheim', batch_number: 'MX-2024-01', expiry_date: '2025-09-01', is_active: true, is_low_stock: true, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
    { id: 'inv_maropitant', name: 'Maropitant 16mg', category: 'medication', description: null, unit: 'tablet', quantity: 8, min_quantity: 15, price_per_unit: 2.5, supplier: 'Zoetis', batch_number: 'MP-2024-01', expiry_date: '2025-05-01', is_active: true, is_low_stock: true, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
    { id: 'inv_lrs', name: 'Fluid — LRS 1L', category: 'supply', description: null, unit: 'bag', quantity: 14, min_quantity: 10, price_per_unit: 4.0, supplier: 'Baxter', batch_number: 'LRS-2024-01', expiry_date: '2025-08-01', is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
    { id: 'inv_syringes', name: 'Syringes 3ml', category: 'supply', description: null, unit: 'each', quantity: 300, min_quantity: 100, price_per_unit: 0.12, supplier: 'BD', batch_number: null, expiry_date: null, is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
    { id: 'inv_gloves', name: 'Surgical Gloves (Size 7)', category: 'supply', description: null, unit: 'pair', quantity: 50, min_quantity: 40, price_per_unit: 0.35, supplier: 'Medline', batch_number: null, expiry_date: null, is_active: true, is_low_stock: false, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
    { id: 'inv_renal', name: 'Prescription Diet — Renal', category: 'food', description: null, unit: 'bag', quantity: 4, min_quantity: 5, price_per_unit: 22.5, supplier: 'Hill\'s Pet Nutrition', batch_number: 'RD-2024-01', expiry_date: '2025-04-01', is_active: true, is_low_stock: true, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
    { id: 'inv_usgel', name: 'Ultrasound Gel', category: 'supply', description: null, unit: 'bottle', quantity: 3, min_quantity: 5, price_per_unit: 8.0, supplier: 'Parker Labs', batch_number: null, expiry_date: null, is_active: true, is_low_stock: true, created_at: fmt(at(7, 0)), updated_at: fmt(at(7, 0)) },
  ]
  invoices = []
  invoiceItems = []
  clinicalNotes = []
  inventoryUpdateLog = []
  noteSeq = 0
}

export function computeVetDashboard(): VetDashboard {
  const today = appointments.filter((a) => a.status !== 'cancelled')
  return {
    today_appointments: today.length,
    pending_notes: clinicalNotes.filter((n) => n.status === 'processing').length,
    checked_in_patients: today.filter((a) => a.status === 'checked_in').length,
    urgent_cases: today.filter((a) => a.is_urgent && a.status !== 'completed').length,
  }
}

export function computeStaffDashboard(): StaffDashboard {
  return {
    today_appointments: appointments.filter((a) => a.status !== 'cancelled').length,
    low_stock_items: inventory.filter((i) => i.is_low_stock).length,
    pending_invoices: invoices.filter((i) => i.status === 'pending').length,
    checked_in_patients: appointments.filter((a) => a.status === 'checked_in').length,
  }
}
