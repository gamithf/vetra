import axios from 'axios'
import { API_BASE_URL, API_PREFIX } from './constants'

const api = axios.create({
  baseURL: `${API_BASE_URL}${API_PREFIX}`,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('vetra_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('vetra_token')
      localStorage.removeItem('vetra_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

export default api

// ── Types ─────────────────────────────────────────────────

export interface User {
  id: string
  email: string
  full_name: string
  role: 'vet' | 'staff' | 'admin'
  phone: string | null
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  full_name: string
  role: string
}

export interface Owner {
  id: string
  first_name: string
  last_name: string
  email: string | null
  phone: string | null
  address: string | null
  notes: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Pet {
  id: string
  owner_id: string
  name: string
  species: string
  breed: string | null
  color: string | null
  gender: string
  date_of_birth: string | null
  weight_kg: number | null
  microchip_id: string | null
  photo_url: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Appointment {
  id: string
  pet_id: string
  vet_id: string | null
  owner_id: string
  room_id: string | null
  start_time: string
  end_time: string
  status: string
  reason: string | null
  notes: string | null
  is_urgent: boolean
  created_at: string
  updated_at: string
}

export interface VetDashboard {
  today_appointments: number
  pending_notes: number
  checked_in_patients: number
  urgent_cases: number
}

export interface StaffDashboard {
  today_appointments: number
  low_stock_items: number
  pending_invoices: number
  checked_in_patients: number
}

export interface InventoryItem {
  id: string
  name: string
  category: string
  description: string | null
  unit: string
  quantity: number
  min_quantity: number
  price_per_unit: number | null
  supplier: string | null
  batch_number: string | null
  expiry_date: string | null
  is_active: boolean
  is_low_stock: boolean
  created_at: string
  updated_at: string
}

export interface MedicalRecord {
  id: string
  pet_id: string
  vet_id: string | null
  appointment_id: string | null
  record_type: string
  diagnosis: string | null
  treatment: string | null
  notes: string | null
  recorded_at: string
  created_at: string
}

export interface ClinicalNote {
  id: string
  pet_id: string
  appointment_id: string | null
  vet_id: string
  raw_transcript: string
  structured_note: string | null
  status: string
  ai_model_version: string | null
  is_edited: boolean
  reviewed_by: string | null
  created_at: string
  updated_at: string
}

export interface SubmitNoteResponse {
  note: ClinicalNote
  appointment_status: string
  medical_record_id: string | null
  message: string
}

export interface Invoice {
  id: string
  appointment_id: string | null
  owner_id: string
  pet_id: string
  total_amount: number
  paid_amount: number
  status: string
  payment_method: string | null
  paid_at: string | null
  due_date: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface InvoiceItem {
  id: string
  invoice_id: string
  description: string
  quantity: number
  unit_price: number
  total_price: number
  notes: string | null
  created_at: string
}

export interface InvoiceWithItems extends Invoice {
  items: InvoiceItem[]
}

// ── API Clients ───────────────────────────────────────────

export const authApi = {
  login: (data: { email: string; password: string }) =>
    api.post<TokenResponse>('/auth/login', data).then(r => r.data),
  register: (data: { email: string; password: string; full_name: string; role: string }) =>
    api.post<TokenResponse>('/auth/register', data).then(r => r.data),
  me: () => api.get<User>('/auth/me').then(r => r.data),
}

export const ownersApi = {
  list: (params?: Record<string, string>) =>
    api.get<Owner[]>('/owners', { params }).then(r => r.data),
  get: (id: string) => api.get<Owner>(`/owners/${id}`).then(r => r.data),
  create: (data: Partial<Owner>) => api.post<Owner>('/owners', data).then(r => r.data),
}

export const petsApi = {
  list: (params?: Record<string, string>) =>
    api.get<Pet[]>('/pets', { params }).then(r => r.data),
  get: (id: string) => api.get<Pet>(`/pets/${id}`).then(r => r.data),
  create: (data: Partial<Pet>) => api.post<Pet>('/pets', data).then(r => r.data),
  medicalRecords: (petId: string) =>
    api.get<MedicalRecord[]>(`/pets/${petId}/medical-records`).then(r => r.data),
}

export const appointmentsApi = {
  list: (params?: Record<string, string>) =>
    api.get<Appointment[]>('/appointments', { params }).then(r => r.data),
  today: () => api.get<Appointment[]>('/appointments/today').then(r => r.data),
  get: (id: string) => api.get<Appointment>(`/appointments/${id}`).then(r => r.data),
  create: (data: Partial<Appointment>) => api.post<Appointment>('/appointments', data).then(r => r.data),
  checkIn: (id: string) => api.post<Appointment>(`/appointments/${id}/check-in`).then(r => r.data),
  start: (id: string) => api.post<Appointment>(`/appointments/${id}/start`).then(r => r.data),
  complete: (id: string) => api.post<Appointment>(`/appointments/${id}/complete`).then(r => r.data),
  emergency: (data: { pet_id: string; owner_id: string; vet_id?: string; reason?: string }) =>
    api.post<Appointment>('/appointments/emergency', data).then(r => r.data),
  pendingCheckout: () => api.get<Appointment[]>('/appointments/pending-checkout').then(r => r.data),
  createInvoice: (id: string) => api.post<InvoiceWithItems>(`/appointments/${id}/create-invoice`).then(r => r.data),
}

export const clinicalNotesApi = {
  create: (data: { pet_id: string; appointment_id: string; raw_transcript: string }) =>
    api.post<SubmitNoteResponse>('/clinical-notes', data).then(r => r.data),
  list: (params?: Record<string, string>) =>
    api.get<ClinicalNote[]>('/clinical-notes', { params }).then(r => r.data),
}

export const inventoryApi = {
  list: (params?: Record<string, string>) =>
    api.get<InventoryItem[]>('/inventory', { params }).then(r => r.data),
  lowStock: () => api.get<InventoryItem[]>('/inventory/low-stock').then(r => r.data),
}

export const dashboardApi = {
  vet: () => api.get<VetDashboard>('/dashboard/vet').then(r => r.data),
  staff: () => api.get<StaffDashboard>('/dashboard/staff').then(r => r.data),
}

export const invoicesApi = {
  pay: (id: string, data: { payment_method: string }) =>
    api.post<Invoice>(`/invoices/${id}/pay`, data).then(r => r.data),
  get: (id: string) => api.get<InvoiceWithItems>(`/invoices/${id}`).then(r => r.data),
}

export const realApi = {
  authApi,
  ownersApi,
  petsApi,
  appointmentsApi,
  clinicalNotesApi,
  inventoryApi,
  dashboardApi,
  invoicesApi,
}
