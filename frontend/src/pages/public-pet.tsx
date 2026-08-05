import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { PawPrint, Calendar, Weight, Stethoscope, Receipt, ShieldCheck, Loader2, AlertTriangle } from 'lucide-react'
import { publicApi, type PublicPetView } from '@/lib/api'
import { formatCurrency } from '@/lib/format'
import { cn } from '@/lib/utils'

function RecordItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-muted/40 px-3 py-2">
      <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="text-sm font-medium capitalize">{value || '—'}</p>
    </div>
  )
}

export function PublicPetPage() {
  const { token } = useParams()
  const [data, setData] = useState<PublicPetView | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) {
      setError('Missing link')
      setLoading(false)
      return
    }
    publicApi.pet(token)
      .then(setData)
      .catch(() => setError('This link is invalid or has expired.'))
      .finally(() => setLoading(false))
  }, [token])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-muted/20">
        <Loader2 size={28} className="animate-spin text-primary" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-muted/20 p-6">
        <div className="w-full max-w-sm rounded-2xl border bg-card p-8 text-center shadow-xl">
          <AlertTriangle size={32} className="mx-auto mb-4 text-amber-500" />
          <h1 className="text-lg font-bold">Link unavailable</h1>
          <p className="mt-2 text-sm text-muted-foreground">{error || 'Unable to load.'}</p>
          <p className="mt-4 text-xs text-muted-foreground">
            Please contact your veterinary clinic for a fresh link.
          </p>
        </div>
      </div>
    )
  }

  const { pet, owner, appointment, invoice, recent_records } = data

  return (
    <div className="min-h-screen bg-muted/20 py-10">
      <div className="mx-auto w-full max-w-2xl space-y-4 px-4">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
              <PawPrint size={16} className="text-primary" />
            </span>
            Vetra
          </div>
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-3 py-1 text-[11px] font-medium text-emerald-700">
            <ShieldCheck size={12} /> Secure pet link
          </span>
        </header>

        <div className="rounded-2xl border bg-card p-6 shadow-lg">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-2xl font-bold text-primary">
              {pet.name[0].toUpperCase()}
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold">{pet.name}</h1>
              <p className="text-sm capitalize text-muted-foreground">
                {pet.species} {pet.breed ? `· ${pet.breed}` : ''} · {pet.gender}
              </p>
              {owner && (
                <p className="mt-0.5 text-xs text-muted-foreground">
                  Owner: {owner.first_name} {owner.last_name}
                </p>
              )}
            </div>
            {pet.weight_kg && (
              <div className="flex items-center gap-1.5 rounded-lg bg-muted/50 px-3 py-2 text-sm">
                <Weight size={14} className="text-muted-foreground" />
                <span className="font-medium">{pet.weight_kg} kg</span>
              </div>
            )}
          </div>

          <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-4">
            <RecordItem label="Species" value={pet.species} />
            <RecordItem label="Breed" value={pet.breed || '—'} />
            <RecordItem label="Colour" value={pet.color || '—'} />
            <RecordItem label="DOB" value={pet.date_of_birth || '—'} />
          </div>
        </div>

        {appointment?.reason && (
          <div className="rounded-2xl border bg-card p-6 shadow-lg">
            <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <Stethoscope size={16} className="text-primary" /> Latest Visit
            </h2>
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">{appointment.reason}</p>
              {appointment.start_time && (
                <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                  <Calendar size={12} />
                  {new Date(appointment.start_time).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
        )}

        {invoice && (
          <div className="rounded-2xl border bg-card p-6 shadow-lg">
            <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold">
              <Receipt size={16} className="text-emerald-500" /> Bill
            </h2>
            <div className="divide-y rounded-lg border">
              {invoice.items.map((item, i) => (
                <div key={i} className="flex items-center justify-between px-4 py-2.5 text-sm">
                  <span>{item.description}</span>
                  <span className="font-medium tabular-nums">
                    {item.quantity > 1 && `${item.quantity} × `}{formatCurrency(item.unit_price)}
                  </span>
                </div>
              ))}
              <div className="flex items-center justify-between bg-muted/30 px-4 py-3 text-sm font-bold">
                <span>Total</span>
                <span>{formatCurrency(invoice.total_amount || 0)}</span>
              </div>
            </div>
            {invoice.status && (
              <p className="mt-3 text-xs capitalize text-muted-foreground">
                Status: <span className={cn('font-medium', invoice.status === 'paid' ? 'text-emerald-600' : 'text-amber-600')}>{invoice.status}</span>
              </p>
            )}
          </div>
        )}

        {recent_records.length > 0 && (
          <div className="rounded-2xl border bg-card p-6 shadow-lg">
            <h2 className="mb-3 text-sm font-semibold">Medical History</h2>
            <div className="space-y-3">
              {recent_records.map((r, i) => (
                <div key={i} className="rounded-lg border-l-2 border-primary/40 bg-muted/30 px-3 py-2">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">{r.record_type}</span>
                    {r.recorded_at && <span className="text-xs text-muted-foreground">{new Date(r.recorded_at).toLocaleDateString()}</span>}
                  </div>
                  {r.diagnosis && <p className="mt-1 text-sm font-medium">{r.diagnosis}</p>}
                  {r.treatment && <p className="text-sm text-muted-foreground">{r.treatment}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        <p className="pb-6 pt-2 text-center text-[11px] text-muted-foreground">
          This page contains private pet information. Do not share this link.
        </p>
      </div>
    </div>
  )
}
