import { useState, useEffect, useCallback } from 'react'
import {
  Clock, AlertTriangle, Activity, Weight, Syringe, Beaker, FileText,
  ChevronRight, PawPrint, Loader2, CheckCircle2, Pill, Calendar,
  PlayCircle, RefreshCw,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Spinner } from '@/components/ui/spinner'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import type { Appointment, Pet, MedicalRecord, VetDashboard } from '@/lib/api'
import { useApi } from '@/lib/use-api'
import { CopilotWidget } from '@/components/copilot-widget'
import { useAuth } from '@/context/auth-context'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

const statusConfig: Record<string, { label: string; color: string; dot: string }> = {
  scheduled: { label: 'Scheduled', color: 'bg-blue-100 text-blue-800 border-blue-200', dot: 'bg-blue-500' },
  checked_in: { label: 'Checked In', color: 'bg-amber-100 text-amber-800 border-amber-200', dot: 'bg-amber-500' },
  in_progress: { label: 'In Progress', color: 'bg-emerald-100 text-emerald-800 border-emerald-200', dot: 'bg-emerald-500' },
  completed: { label: 'Completed', color: 'bg-slate-100 text-slate-600 border-slate-200', dot: 'bg-slate-400' },
  cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-800 border-red-200', dot: 'bg-red-500' },
}

function formatTime(d: string) {
  const t = new Date(d)
  return `${t.getHours().toString().padStart(2, '0')}:${t.getMinutes().toString().padStart(2, '0')}`
}

function AppointmentCard({
  appointment, petName, selected, onClick, popIn,
}: {
  appointment: Appointment
  petName: string
  selected: boolean
  onClick: () => void
  popIn: boolean
}) {
  const cfg = statusConfig[appointment.status] || statusConfig.scheduled
  return (
    <div
      onClick={onClick}
      className={cn(
        'flex cursor-pointer items-center gap-4 rounded-lg border p-4 transition-all duration-200 hover:shadow-md',
        appointment.is_urgent && 'border-l-4 border-l-red-500 bg-red-50/30',
        appointment.status === 'checked_in' && 'bg-amber-50/30',
        selected && 'ring-2 ring-primary shadow-md',
        popIn && 'animate-[popIn_0.5s_ease-out]',
      )}
    >
      <div className="flex min-w-[48px] flex-col items-center">
        <span className="text-sm font-bold tabular-nums">{formatTime(appointment.start_time)}</span>
        <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
          {new Date(appointment.start_time).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
        </span>
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="truncate font-semibold">{petName}</span>
          {appointment.is_urgent && (
            <Badge variant="destructive" className="gap-1 px-1.5 py-0 text-[10px]">
              <AlertTriangle size={10} /> URGENT
            </Badge>
          )}
        </div>
        <p className="mt-0.5 truncate text-sm text-muted-foreground">{appointment.reason || 'General check-up'}</p>
      </div>
      <div className={cn('flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium', cfg.color)}>
        <span className={cn('h-1.5 w-1.5 rounded-full', cfg.dot)} />
        {cfg.label}
      </div>
    </div>
  )
}

function PatientEMR({
  petId, appointment, onBack, onRefresh,
}: {
  petId: string
  appointment: Appointment | null
  onBack: () => void
  onRefresh: () => void
}) {
  const { petsApi } = useApi()
  const [records, setRecords] = useState<MedicalRecord[]>([])
  const [pet, setPet] = useState<Pet | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    Promise.all([
      petsApi.get(petId),
      petsApi.medicalRecords(petId),
    ])
      .then(([p, r]) => { setPet(p); setRecords(r) })
      .catch(() => toast.error('Failed to load patient records'))
      .finally(() => setLoading(false))
  }, [petId])

  useEffect(() => { load() }, [load])

  const { appointmentsApi } = useApi()
  const handleStart = async () => {
    if (!appointment) return
    setActionLoading('start')
    try {
      await appointmentsApi.start(appointment.id)
      toast.success('Appointment started')
      onRefresh()
    } catch { toast.error('Failed to start') }
    finally { setActionLoading(null) }
  }

  const handleComplete = async () => {
    if (!appointment) return
    setActionLoading('complete')
    try {
      await appointmentsApi.complete(appointment.id)
      toast.success('Appointment completed — Submit notes to finalize')
      onRefresh()
    } catch { toast.error('Failed to complete') }
    finally { setActionLoading(null) }
  }

  if (loading) return <Spinner className="py-20" />

  if (!pet) return <p className="py-10 text-center text-muted-foreground">Patient not found</p>

  const recordIcons: Record<string, React.ReactNode> = {
    examination: <Activity size={16} />, vaccination: <Syringe size={16} />,
    surgery: <Pill size={16} />, lab_work: <Beaker size={16} />,
  }

  return (
    <div className="animate-in space-y-4">
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={onBack} className="-ml-2 gap-2">
          <ChevronRight size={16} className="rotate-180" /> Back to queue
        </Button>
        <Button variant="ghost" size="icon" onClick={load}><RefreshCw size={16} /></Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <Avatar className="h-14 w-14">
              <AvatarFallback className="bg-primary/10 text-lg text-primary">{pet.name[0].toUpperCase()}</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <CardTitle className="text-xl">{pet.name}</CardTitle>
              <CardDescription className="capitalize">
                {pet.species} {pet.breed ? `· ${pet.breed}` : ''} · {pet.gender}
                {pet.weight_kg ? ` · ${pet.weight_kg} kg` : ''}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              {appointment?.status === 'checked_in' && (
                <Button size="sm" onClick={handleStart} disabled={actionLoading === 'start'} className="gap-1.5">
                  {actionLoading === 'start' ? <Loader2 size={14} className="animate-spin" /> : <PlayCircle size={14} />}
                  Start Exam
                </Button>
              )}
              {appointment?.status === 'in_progress' && (
                <Button size="sm" variant="outline" onClick={handleComplete} disabled={actionLoading === 'complete'} className="gap-1.5">
                  {actionLoading === 'complete' ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle2 size={14} />}
                  Complete
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-3">
          <div className="flex items-center gap-2 rounded-lg bg-muted/50 p-3">
            <Weight size={16} className="text-muted-foreground" />
            <div><p className="text-xs text-muted-foreground">Weight</p><p className="font-medium">{pet.weight_kg || '—'} kg</p></div>
          </div>
          <div className="flex items-center gap-2 rounded-lg bg-muted/50 p-3">
            <Calendar size={16} className="text-muted-foreground" />
            <div><p className="text-xs text-muted-foreground">DOB</p><p className="font-medium">{pet.date_of_birth || '—'}</p></div>
          </div>
          <div className="flex items-center gap-2 rounded-lg bg-muted/50 p-3">
            <Syringe size={16} className="text-muted-foreground" />
            <div><p className="text-xs text-muted-foreground">Microchip</p><p className="font-medium">{pet.microchip_id || '—'}</p></div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <FileText size={18} className="text-primary" /> Medical Timeline
          </CardTitle>
          <CardDescription>{records.length} records</CardDescription>
        </CardHeader>
        <CardContent>
          {records.length === 0 ? (
            <p className="py-8 text-center text-muted-foreground">No medical records yet</p>
          ) : (
            <div className="relative space-y-0">
              {records.map((record, i) => (
                <div key={record.id} className={cn('relative flex gap-4 pb-6 last:pb-0', i === records.length - 1 && 'animate-[popIn_0.5s_ease-out]')}>
                  <div className="flex flex-col items-center">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-primary/20 bg-primary/5 text-primary">
                      {recordIcons[record.record_type] || <FileText size={14} />}
                    </div>
                    {i < records.length - 1 && <div className="w-px flex-1 bg-border" />}
                  </div>
                  <div className="flex-1 pt-1">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-[10px] uppercase">{record.record_type}</Badge>
                      <span className="text-xs text-muted-foreground">{new Date(record.recorded_at).toLocaleDateString()}</span>
                    </div>
                    {record.diagnosis && <p className="mt-1 text-sm font-medium">{record.diagnosis}</p>}
                    {record.treatment && <p className="text-sm text-muted-foreground">{record.treatment}</p>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export function VetDashboard() {
  const { appointmentsApi, dashboardApi, petsApi } = useApi()
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [dashData, setDashData] = useState<VetDashboard>({ today_appointments: 0, pending_notes: 0, checked_in_patients: 0, urgent_cases: 0 })
  const [petNames, setPetNames] = useState<Record<string, string>>({})
  const [checkedInIds, setCheckedInIds] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [selectedAppt, setSelectedAppt] = useState<Appointment | null>(null)
  const { user } = useAuth()

  const load = useCallback(async () => {
    try {
      const [apps, dash, pets] = await Promise.all([
        appointmentsApi.today(),
        dashboardApi.vet(),
        petsApi.list({}),
      ])
      const nameMap: Record<string, string> = {}
      pets.forEach((p) => { nameMap[p.id] = p.name })
      setPetNames(nameMap)
      const prev = new Set(appointments.filter((a) => a.status === 'checked_in').map((a) => a.id))
      const sorted = [...apps].sort((a, b) => {
        if (a.is_urgent !== b.is_urgent) return a.is_urgent ? -1 : 1
        return new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
      })
      const newChecked = new Set(sorted.filter((a) => a.status === 'checked_in').map((a) => a.id))
      const popIn = new Set([...newChecked].filter((id) => !prev.has(id)))
      setCheckedInIds(popIn)
      setAppointments(sorted)
      setDashData(dash)
      setTimeout(() => setCheckedInIds(new Set()), 800)
    } catch { toast.error('Failed to load dashboard') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const handleNoteSubmitted = () => {
    load()
    setSelectedAppt(null)
  }

  const selectedPetName = selectedAppt ? petNames[selectedAppt.pet_id] : null

  if (loading) return <div className="flex min-h-[60vh] items-center justify-center"><Spinner size="lg" /></div>

  return (
    <div className="animate-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Good {new Date().getHours() < 12 ? 'morning' : 'afternoon'}, {user?.full_name?.split(' ')[0]}</h1>
          <p className="text-muted-foreground">Today&apos;s patient overview</p>
        </div>
        <Button variant="outline" size="sm" onClick={load} className="gap-1.5">
          <RefreshCw size={14} /> Refresh
        </Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Appointments</CardTitle><Calendar size={16} className="text-muted-foreground" />
          </CardHeader>
          <CardContent><div className="text-2xl font-bold">{dashData.today_appointments}</div><p className="text-xs text-muted-foreground">scheduled today</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Checked In</CardTitle><CheckCircle2 size={16} className="text-amber-500" />
          </CardHeader>
          <CardContent><div className="text-2xl font-bold">{dashData.checked_in_patients}</div><p className="text-xs text-muted-foreground">waiting in rooms</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Urgent Cases</CardTitle><AlertTriangle size={16} className="text-red-500" />
          </CardHeader>
          <CardContent><div className="text-2xl font-bold text-red-600">{dashData.urgent_cases}</div><p className="text-xs text-muted-foreground">needs immediate attention</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Pending Notes</CardTitle><FileText size={16} className="text-muted-foreground" />
          </CardHeader>
          <CardContent><div className="text-2xl font-bold">{dashData.pending_notes}</div><p className="text-xs text-muted-foreground">awaiting AI processing</p></CardContent>
        </Card>
      </div>

      {!selectedAppt ? (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">Patient Queue</h2>
          {appointments.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center py-16">
                <PawPrint size={48} className="mb-4 text-muted-foreground/30" />
                <p className="text-lg font-medium">No appointments today</p>
                <p className="text-sm text-muted-foreground">Enjoy your day!</p>
              </CardContent>
            </Card>
          ) : (
            appointments.map((apt) => (
              <AppointmentCard
                key={apt.id}
                appointment={apt}
                petName={petNames[apt.pet_id] || `Patient #${apt.pet_id.slice(0, 8)}`}
                selected={selectedAppt?.id === apt.id}
                popIn={checkedInIds.has(apt.id)}
                onClick={() => setSelectedAppt(apt)}
              />
            ))
          )}
        </div>
      ) : (
        <PatientEMR
          petId={selectedAppt.pet_id}
          appointment={selectedAppt}
          onBack={() => setSelectedAppt(null)}
          onRefresh={load}
        />
      )}

      <CopilotWidget
        activePatientId={selectedAppt?.pet_id ?? null}
        activePatientName={selectedPetName}
        activeAppointmentId={selectedAppt?.id ?? null}
        onNoteSubmitted={handleNoteSubmitted}
      />
    </div>
  )
}
