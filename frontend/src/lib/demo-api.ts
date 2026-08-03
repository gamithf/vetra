import { sleep, demoState, computeVetDashboard, computeStaffDashboard } from './demo'
import type {
  User, Owner, Pet, Appointment, MedicalRecord, ClinicalNote, InventoryItem,
  Invoice, InvoiceItem, VetDashboard, StaffDashboard, TokenResponse,
  SubmitNoteResponse, InvoiceWithItems,
} from './api'

// Realistic network-ish delay so UI spinners/animations read naturally.
const delay = 350

function clone<T>(v: T): T {
  return JSON.parse(JSON.stringify(v))
}

function makeToken(user: User): TokenResponse {
  return {
    access_token: 'demo.' + btoa(JSON.stringify({ sub: user.id })).replace(/=+$/, ''),
    token_type: 'bearer',
    user: clone(user),
  }
}

export const demoAuthApi = {
  login: async ({ email }: { email: string; password: string }): Promise<TokenResponse> => {
    await sleep(delay)
    const isVet = email.includes('vet')
    return makeToken(isVet ? demoState.demoVetUser : demoState.demoUser)
  },
  register: async (data: { email: string; password: string; full_name: string; role: string }): Promise<TokenResponse> => {
    await sleep(delay)
    const user: User = { id: 'usr_new', email: data.email, full_name: data.full_name, role: data.role as User['role'], phone: null, is_active: true, created_at: new Date().toISOString() }
    return makeToken(user)
  },
  me: async (): Promise<User> => {
    const stored = typeof window !== 'undefined' ? localStorage.getItem('vetra_user') : null
    if (stored) return JSON.parse(stored) as User
    return clone(demoState.demoUser)
  },
}

export const demoOwnersApi = {
  list: async (): Promise<Owner[]> => {
    await sleep(delay)
    return clone(demoState.owners)
  },
  get: async (id: string): Promise<Owner> => {
    await sleep(delay)
    return clone(demoState.owners.find((o) => o.id === id)!)
  },
  create: async (data: Partial<Owner>): Promise<Owner> => {
    await sleep(delay)
    const owner: Owner = { id: 'own_' + Math.random().toString(36).slice(2, 8), first_name: data.first_name || '', last_name: data.last_name || '', email: data.email || null, phone: data.phone || null, address: null, notes: null, is_active: true, created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
    return owner
  },
}

export const demoPetsApi = {
  list: async (params?: Record<string, string>): Promise<Pet[]> => {
    await sleep(delay)
    let list = clone(demoState.pets)
    if (params?.owner_id) list = list.filter((p) => p.owner_id === params.owner_id)
    return list
  },
  get: async (id: string): Promise<Pet> => {
    await sleep(delay)
    return clone(demoState.pets.find((p) => p.id === id)!)
  },
  create: async (data: Partial<Pet>): Promise<Pet> => {
    await sleep(delay)
    const pet: Pet = { id: 'pet_' + Math.random().toString(36).slice(2, 8), owner_id: data.owner_id || '', name: data.name || '', species: data.species || 'dog', breed: null, color: null, gender: data.gender || 'unknown', date_of_birth: null, weight_kg: null, microchip_id: null, photo_url: null, is_active: true, created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
    return pet
  },
  medicalRecords: async (petId: string): Promise<MedicalRecord[]> => {
    await sleep(delay)
    return clone(demoState.medicalRecords.filter((r) => r.pet_id === petId).sort((a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime()))
  },
}

export const demoAppointmentsApi = {
  list: async (): Promise<Appointment[]> => {
    await sleep(delay)
    return clone([...demoState.appointments].sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime()))
  },
  today: async (): Promise<Appointment[]> => {
    await sleep(delay)
    const sorted = [...demoState.appointments].sort((a, b) => {
      if (a.is_urgent !== b.is_urgent) return a.is_urgent ? -1 : 1
      return new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
    })
    return clone(sorted)
  },
  get: async (id: string): Promise<Appointment> => {
    await sleep(delay)
    return clone(demoState.appointments.find((a) => a.id === id)!)
  },
  create: async (data: Partial<Appointment>): Promise<Appointment> => {
    await sleep(delay)
    const apt: Appointment = { id: 'apt_' + Math.random().toString(36).slice(2, 8), pet_id: data.pet_id || '', vet_id: null, owner_id: data.owner_id || '', room_id: null, start_time: data.start_time || new Date().toISOString(), end_time: data.end_time || new Date().toISOString(), status: 'scheduled', reason: data.reason || null, notes: null, is_urgent: false, created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
    demoState.appointments = [...demoState.appointments, apt]
    return clone(apt)
  },
  checkIn: async (id: string): Promise<Appointment> => {
    await sleep(delay)
    const apt = demoState.appointments.find((a) => a.id === id)!
    apt.status = 'checked_in'
    apt.updated_at = new Date().toISOString()
    return clone(apt)
  },
  start: async (id: string): Promise<Appointment> => {
    await sleep(delay)
    const apt = demoState.appointments.find((a) => a.id === id)!
    apt.status = 'in_progress'
    apt.updated_at = new Date().toISOString()
    return clone(apt)
  },
  complete: async (id: string): Promise<Appointment> => {
    await sleep(delay)
    const apt = demoState.appointments.find((a) => a.id === id)!
    apt.status = 'completed'
    apt.updated_at = new Date().toISOString()
    return clone(apt)
  },
  emergency: async (data: { pet_id: string; owner_id: string; vet_id?: string; reason?: string }): Promise<Appointment> => {
    await sleep(delay)
    const apt: Appointment = { id: 'apt_' + Math.random().toString(36).slice(2, 8), pet_id: data.pet_id, vet_id: null, owner_id: data.owner_id, room_id: null, start_time: new Date().toISOString(), end_time: new Date().toISOString(), status: 'checked_in', reason: data.reason || 'Emergency', notes: 'EMERGENCY INTAKE', is_urgent: true, created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
    demoState.appointments = [...demoState.appointments, apt]
    return clone(apt)
  },
  pendingCheckout: async (): Promise<Appointment[]> => {
    await sleep(delay)
    return clone(demoState.appointments.filter((a) => a.status === 'completed' && !demoState.invoices.some((i) => i.appointment_id === a.id)))
  },
  createInvoice: async (id: string): Promise<InvoiceWithItems> => {
    await sleep(delay)
    const apt = demoState.appointments.find((a) => a.id === id)!
    const existing = demoState.invoices.find((i) => i.appointment_id === id)
    if (existing) {
      return clone({ ...existing, items: demoState.invoiceItems.filter((it) => it.invoice_id === existing.id) } as InvoiceWithItems)
    }
    const items: InvoiceItem[] = [
      { id: 'invit_001', invoice_id: 'inv_demo', description: 'Annual Wellness Exam', quantity: 1, unit_price: 55.0, total_price: 55.0, notes: null, created_at: new Date().toISOString() },
      { id: 'invit_002', invoice_id: 'inv_demo', description: 'DAPP Vaccine', quantity: 1, unit_price: 18.5, total_price: 18.5, notes: null, created_at: new Date().toISOString() },
      { id: 'invit_003', invoice_id: 'inv_demo', description: 'Office Visit Fee', quantity: 1, unit_price: 11.5, total_price: 11.5, notes: null, created_at: new Date().toISOString() },
    ]
    const total = items.reduce((s, it) => s + it.total_price, 0)
    const inv: Invoice = { id: 'inv_demo', appointment_id: id, owner_id: apt.owner_id, pet_id: apt.pet_id, total_amount: total, paid_amount: 0, status: 'pending', payment_method: null, paid_at: null, due_date: null, notes: null, created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
    demoState.invoices = [...demoState.invoices, inv]
    demoState.invoiceItems = [...demoState.invoiceItems, items.map((it) => ({ ...it, invoice_id: inv.id }))]
    return clone({ ...inv, items: demoState.invoiceItems.filter((it) => it.invoice_id === inv.id) } as InvoiceWithItems)
  },
}

export const demoClinicalNotesApi = {
  create: async (data: { pet_id: string; appointment_id: string; raw_transcript: string }): Promise<SubmitNoteResponse> => {
    await sleep(400)
    const id = demoState.nextNoteId()
    const note: ClinicalNote = {
      id, pet_id: data.pet_id, appointment_id: data.appointment_id, vet_id: 'usr_002',
      raw_transcript: data.raw_transcript,
      structured_note: 'Simulated AI: Max presented for annual wellness exam. Healthy — no issues found. Routine vaccination administered. Preventative care recommended.',
      status: 'completed', ai_model_version: 'vetra-ai-v1', is_edited: false, reviewed_by: null,
      created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
    }
    demoState.clinicalNotes = [...demoState.clinicalNotes, note]

    const record: MedicalRecord = {
      id: 'rec_' + Math.random().toString(36).slice(2, 8), pet_id: data.pet_id, vet_id: 'usr_vet1',
      appointment_id: data.appointment_id, record_type: 'examination', diagnosis: 'Healthy — no issues found',
      treatment: 'DAPP vaccine administered, 1ml IM. Dental cleaning recommended.', notes: data.raw_transcript.slice(0, 200),
      recorded_at: new Date().toISOString(), created_at: new Date().toISOString(),
    }
    demoState.medicalRecords = [...demoState.medicalRecords, record]

    // Simulate inventory decrement — the DAPP vaccine used during Max's visit
    const target = demoState.inventory.find((i) => i.id === 'inv_dapp')
    if (target) {
      target.quantity = Math.max(0, target.quantity - 1)
      target.is_low_stock = target.quantity < target.min_quantity
      target.updated_at = new Date().toISOString()
      demoState.inventoryUpdateLog = [...demoState.inventoryUpdateLog, `-1 dose DAPP Vaccine`]
    }

    // Mark appointment completed
    const apt = demoState.appointments.find((a) => a.id === data.appointment_id)
    if (apt && apt.status !== 'completed') {
      apt.status = 'completed'
      apt.updated_at = new Date().toISOString()
    }

    return { note, appointment_status: 'completed', medical_record_id: record.id, message: 'Visit recorded — medical record created, inventory updated, and bill generated.' }
  },
  list: async (): Promise<ClinicalNote[]> => {
    await sleep(delay)
    return clone([...demoState.clinicalNotes].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()))
  },
}

export const demoInventoryApi = {
  list: async (): Promise<InventoryItem[]> => {
    await sleep(delay)
    return clone(demoState.inventory)
  },
  lowStock: async (): Promise<InventoryItem[]> => {
    await sleep(delay)
    return clone(demoState.inventory.filter((i) => i.is_low_stock))
  },
}

export const demoDashboardApi = {
  vet: async (): Promise<VetDashboard> => {
    await sleep(delay)
    return clone(computeVetDashboard())
  },
  staff: async (): Promise<StaffDashboard> => {
    await sleep(delay)
    return clone(computeStaffDashboard())
  },
}

export const demoInvoicesApi = {
  pay: async (id: string, data: { payment_method: string }): Promise<Invoice> => {
    await sleep(600)
    const inv = demoState.invoices.find((i) => i.id === id)!
    inv.status = 'paid'
    inv.paid_amount = inv.total_amount
    inv.payment_method = data.payment_method
    inv.paid_at = new Date().toISOString()
    inv.updated_at = new Date().toISOString()
    return clone(inv)
  },
  get: async (id: string): Promise<InvoiceWithItems> => {
    await sleep(delay)
    const inv = demoState.invoices.find((i) => i.id === id)!
    return clone({ ...inv, items: demoState.invoiceItems.filter((it) => it.invoice_id === id) } as InvoiceWithItems)
  },
}

export const demoApi = {
  authApi: demoAuthApi,
  ownersApi: demoOwnersApi,
  petsApi: demoPetsApi,
  appointmentsApi: demoAppointmentsApi,
  clinicalNotesApi: demoClinicalNotesApi,
  inventoryApi: demoInventoryApi,
  dashboardApi: demoDashboardApi,
  invoicesApi: demoInvoicesApi,
}
