import { useState, useEffect, useCallback } from 'react'
import { CalendarDays, CalendarPlus, Plus, RefreshCw, Stethoscope } from 'lucide-react'
import { publicApi, type PublicPortal, type PublicPetInfo, type PublicAppointment } from '@/lib/api'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'

const CLINIC_HOURS = 'Clinic hours: Mon–Fri 9:00–17:00 · Sat & Sun 9:00–12:00'

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })
}

function fmtTime(iso: string) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function todayStr() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function maxDateStr() {
  const d = new Date()
  d.setDate(d.getDate() + 30)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function SlotGrid({
  slots, selected, onSelect, secondsPerSlot,
}: {
  slots: string[]
  selected: string | null
  onSelect: (iso: string) => void
  secondsPerSlot: number
}) {
  if (slots.length === 0) {
    return <p className="text-sm text-muted-foreground">No free slots on this day. Try another date.</p>
  }
  return (
    <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
      {slots.map((iso) => {
        const secs = Math.floor(new Date(iso).getTime() / 1000)
        const isPast = secs < secondsPerSlot
        return (
          <button
            key={iso}
            type="button"
            disabled={isPast}
            onClick={() => onSelect(iso)}
            className={cn(
              'rounded-lg border px-3 py-2 text-sm font-medium transition-all cursor-pointer disabled:cursor-not-allowed disabled:opacity-40',
              selected === iso
                ? 'border-primary bg-primary text-primary-foreground'
                : 'border-input bg-background hover:border-primary/50 hover:bg-muted',
            )}
          >
            {fmtTime(iso)}
          </button>
        )
      })}
    </div>
  )
}

function AppointmentsList({
  appointments, onReschedule,
}: {
  appointments: PublicAppointment[]
  onReschedule: (a: PublicAppointment) => void
}) {
  if (appointments.length === 0) {
    return (
      <div className="flex flex-col items-center rounded-lg border border-dashed py-10 text-center">
        <CalendarDays size={32} className="mb-2 text-muted-foreground/40" />
        <p className="text-sm font-medium">No appointments yet</p>
        <p className="text-xs text-muted-foreground">Book one below.</p>
      </div>
    )
  }
  const now = Date.now()
  const sorted = [...appointments].sort((a, b) =>
    new Date(a.start_time).getTime() - new Date(b.start_time).getTime(),
  )
  const statusLabel: Record<string, string> = {
    scheduled: 'Scheduled',
    checked_in: 'Checked in',
    in_progress: 'In progress',
    completed: 'Completed',
    cancelled: 'Cancelled',
    no_show: 'Missed',
  }
  const statusColor: Record<string, string> = {
    scheduled: 'bg-blue-100 text-blue-700',
    checked_in: 'bg-amber-100 text-amber-700',
    in_progress: 'bg-emerald-100 text-emerald-700',
    completed: 'bg-slate-100 text-slate-600',
    cancelled: 'bg-red-100 text-red-600',
    no_show: 'bg-red-100 text-red-600',
  }
  return (
    <div className="divide-y rounded-lg border">
      {sorted.map((a) => {
        const isFuture = new Date(a.start_time).getTime() > now
        const canReschedule = isFuture && a.status === 'scheduled'
        return (
          <div key={a.id} className="flex items-center justify-between gap-3 px-4 py-3">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-medium capitalize">{a.pet_name}</span>
                <span className={cn('rounded-full px-2 py-0.5 text-[10px] font-medium capitalize', statusColor[a.status] || 'bg-muted text-muted-foreground')}>
                  {statusLabel[a.status] || a.status}
                </span>
              </div>
              <p className="mt-0.5 text-sm text-muted-foreground">
                {fmtDate(a.start_time)} · {fmtTime(a.start_time)}
                {a.vet_name ? ` · Dr. ${a.vet_name.split(' ').slice(-1)[0]}` : ''}
              </p>
              <p className="truncate text-xs text-muted-foreground/80">{a.reason || 'General check-up'}</p>
            </div>
            {canReschedule && (
              <Button variant="outline" size="sm" onClick={() => onReschedule(a)} className="shrink-0">
                Reschedule
              </Button>
            )}
          </div>
        )
      })}
    </div>
  )
}

interface BookingFormProps {
  token: string
  pets: PublicPetInfo[]
  initial: { pet?: PublicPetInfo; appointment?: PublicAppointment } | null
  onDone: () => void
  onCancel?: () => void
}

function BookingForm({ token, pets, initial, onDone, onCancel }: BookingFormProps) {
  const isReschedule = !!initial?.appointment
  const editing = initial?.appointment ?? null

  const [petId, setPetId] = useState<string>(initial?.pet?.id ?? initial?.appointment?.pet_id ?? pets[0]?.id ?? '')
  const [date, setDate] = useState<string>(todayStr())
  const [slots, setSlots] = useState<string[]>([])
  const [slot, setSlot] = useState<string | null>(null)
  const [reason, setReason] = useState('')
  const [loadingSlots, setLoadingSlots] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const selectedPet = pets.find((p) => p.id === petId) ?? null
  const vetId = editing?.vet_id ?? selectedPet?.primary_vet_id ?? null
  const vetName = editing?.vet_name ?? selectedPet?.primary_vet_name ?? null
  const nowSeconds = Math.floor(Date.now() / 1000)
  const [lastSlotsKey, setLastSlotsKey] = useState('')

  const loadSlots = useCallback(async () => {
    if (!vetId) {
      setSlots([])
      setSlot(null)
      return
    }
    const key = `${petId}|${vetId}|${date}`
    setLastSlotsKey(key)
    setLoadingSlots(true)
    setSlot(null)
    setSlots([])
    try {
      const res = await publicApi.slots(token, vetId, date)
      setSlots(res.slots)
    } catch {
      setSlots([])
    } finally {
      setLoadingSlots(false)
    }
  }, [token, petId, vetId, date])

  useEffect(() => {
    if (editing) {
      const st = editing.start_time
      const d = st.slice(0, 10)
      setDate(d)
      setReason(editing.reason || '')
    }
    loadSlots()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [petId, vetId, date])

  const submit = async () => {
    if (!slot) return
    setSubmitting(true)
    try {
      if (isReschedule && editing) {
        await publicApi.updateAppointment(token, editing.id, {
          pet_id: editing.pet_id,
          vet_id: editing.vet_id ?? vetId,
          start_time: slot,
          reason: reason || undefined,
        })
      } else {
        if (!petId) return
        await publicApi.createAppointment(token, {
          pet_id: petId,
          vet_id: vetId ?? undefined,
          start_time: slot,
          reason: reason || undefined,
        })
      }
      onDone()
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-4">
      {!isReschedule && (
        <div>
          <label className="mb-1 block text-xs font-medium text-muted-foreground">Pet</label>
          <select
            className="flex h-10 w-full items-center rounded-lg border border-input bg-background px-3 text-sm"
            value={petId}
            onChange={(e) => { setPetId(e.target.value); setSlot(null) }}
          >
            {pets.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
      )}

      <div>
        <label className="mb-1 block text-xs font-medium text-muted-foreground">
          {isReschedule ? 'New date' : 'Date'}
        </label>
        <Input
          type="date"
          value={date}
          min={todayStr()}
          max={maxDateStr()}
          onChange={(e) => { setDate(e.target.value); setSlot(null) }}
        />
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">Available times</span>
        {vetName && (
          <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
            <Stethoscope size={12} /> {vetName}
          </span>
        )}
      </div>

      {loadingSlots ? (
        <div className="flex justify-center py-4"><Spinner /></div>
      ) : (
        <SlotGrid slots={slots} selected={slot} onSelect={setSlot} secondsPerSlot={nowSeconds} />
      )}

      <div>
        <label className="mb-1 block text-xs font-medium text-muted-foreground">
          Reason (optional)
        </label>
        <Input
          type="text"
          placeholder={isReschedule ? 'Update reason' : 'e.g. Follow-up for skin condition'}
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />
      </div>

      <div className="flex justify-end gap-2 pt-1">
        {isReschedule && onCancel && (
          <Button type="button" variant="ghost" onClick={onCancel}>Cancel</Button>
        )}
        <Button type="button" onClick={submit} disabled={!slot || submitting} className="gap-1.5">
          {submitting ? <Spinner className="h-4 w-4" /> : null}
          {submitting ? 'Saving…' : isReschedule ? 'Save new time' : 'Book appointment'}
        </Button>
      </div>

      <p className="text-center text-[11px] text-muted-foreground">{CLINIC_HOURS}</p>
    </div>
  )
}

export function PublicBooking({ token }: { token: string }) {
  const [portal, setPortal] = useState<PublicPortal | null>(null)
  const [loading, setLoading] = useState(true)
  const [bookOpen, setBookOpen] = useState(false)
  const [editing, setEditing] = useState<PublicAppointment | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    publicApi.portal(token)
      .then(setPortal)
      .catch(() => setMessage('Could not load your appointments. Please refresh.'))
      .finally(() => setLoading(false))
  }, [token])

  useEffect(() => { load() }, [load])

  useEffect(() => {
    if (!message) return
    const t = setTimeout(() => setMessage(null), 4000)
    return () => clearTimeout(t)
  }, [message])

  const onDone = (msg?: string) => {
    if (msg) setMessage(msg)
    setBookOpen(false)
    setEditing(null)
    load()
  }

  if (loading) {
    return <div className="flex justify-center py-16"><Spinner size="lg" /></div>
  }

  const pets = portal?.pets ?? []

  return (
    <div className="space-y-4">
      {message && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50/60 px-4 py-3 text-sm font-medium text-emerald-800">
          {message}
        </div>
      )}

      <div className="flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-sm font-semibold">
          <CalendarDays size={16} className="text-primary" /> My Appointments
        </h2>
        <Button variant="outline" size="sm" onClick={load} className="gap-1.5">
          <RefreshCw size={14} /> Refresh
        </Button>
      </div>

      <AppointmentsList
        appointments={portal?.appointments ?? []}
        onReschedule={(a) => { setEditing(a); setBookOpen(true) }}
      />

      {bookOpen || (pets.length > 0 && portal && portal.appointments.length === 0) ? (
        <div className="rounded-2xl border bg-card p-5 shadow-sm">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold">
            <CalendarPlus size={16} className="text-primary" />
            {editing ? 'Reschedule appointment' : 'Book a new appointment'}
          </h3>
          <BookingForm
            token={token}
            pets={pets}
            initial={editing ? { appointment: editing } : null}
            onDone={() => onDone(editing ? 'Appointment updated.' : 'Appointment booked.')}
            onCancel={() => { setBookOpen(false); setEditing(null) }}
          />
        </div>
      ) : (
        <Button onClick={() => setBookOpen(true)} className="w-full gap-1.5">
          <Plus size={16} /> Book an appointment
        </Button>
      )}
    </div>
  )
}