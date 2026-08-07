import { useState, useEffect } from 'react'
import { AlertTriangle, Loader2, X, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { Owner, Pet } from '@/lib/api'
import { ownersApi, petsApi, appointmentsApi } from '@/lib/api'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

interface Props {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

export function EmergencyIntakeModal({ open, onClose, onSuccess }: Props) {
  const [step, setStep] = useState<'owner' | 'pet' | 'reason'>('owner')
  const [owners, setOwners] = useState<Owner[]>([])
  const [pets, setPets] = useState<Pet[]>([])
  const [search, setSearch] = useState('')
  const [selectedOwnerId, setSelectedOwnerId] = useState<string | null>(null)
  const [selectedPetId, setSelectedPetId] = useState<string | null>(null)
  const [reason, setReason] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (open) {
      setStep('owner')
      setSelectedOwnerId(null)
      setSelectedPetId(null)
      setReason('')
      setSearch('')
      ownersApi.list().then(setOwners).catch(() => {})
    }
  }, [open])

  useEffect(() => {
    if (selectedOwnerId) {
      petsApi.list({ owner_id: selectedOwnerId }).then(setPets).catch(() => {})
    }
  }, [selectedOwnerId])

  const filteredOwners = owners.filter(
    (o) =>
      `${o.first_name} ${o.last_name}`.toLowerCase().includes(search.toLowerCase()) ||
      o.phone?.includes(search),
  )

  const handleSubmit = async () => {
    if (!selectedPetId || !selectedOwnerId) return
    setSubmitting(true)
    try {
      await appointmentsApi.emergency({
        pet_id: selectedPetId,
        owner_id: selectedOwnerId,
        reason: reason || 'Emergency intake',
      })
      toast.success('Emergency patient checked in')
      onSuccess()
      onClose()
    } catch {
      toast.error('Failed to create emergency intake')
    } finally {
      setSubmitting(false)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <Card className="w-full max-w-lg animate-in shadow-2xl">
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <AlertTriangle size={20} className="text-red-500" />
            Emergency Intake
          </CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X size={18} />
          </Button>
        </CardHeader>
        <CardContent>
          {step === 'owner' && (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">Search and select the owner:</p>
              <div className="relative">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <Input className="pl-9" placeholder="Search by name or phone..." value={search} onChange={(e) => setSearch(e.target.value)} autoFocus />
              </div>
              <div className="max-h-60 space-y-1 overflow-y-auto">
                {filteredOwners.map((o) => (
                  <button
                    key={o.id}
                    onClick={() => { setSelectedOwnerId(o.id); setStep('pet') }}
                    className="flex w-full items-center gap-3 rounded-lg border p-3 text-left text-sm transition-colors hover:bg-accent"
                  >
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary font-medium">
                      {o.first_name[0]}{o.last_name[0]}
                    </div>
                    <div>
                      <p className="font-medium">{o.first_name} {o.last_name}</p>
                      <p className="text-xs text-muted-foreground">{o.phone || o.email}</p>
                    </div>
                  </button>
                ))}
                {filteredOwners.length === 0 && (
                  <p className="py-8 text-center text-sm text-muted-foreground">No owners found</p>
                )}
              </div>
            </div>
          )}

          {step === 'pet' && (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">Select the patient:</p>
              <div className="max-h-60 space-y-1 overflow-y-auto">
                {pets.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => { setSelectedPetId(p.id); setStep('reason') }}
                    className="flex w-full items-center gap-3 rounded-lg border p-3 text-left text-sm transition-colors hover:bg-accent"
                  >
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary font-medium uppercase">
                      {p.name[0]}
                    </div>
                    <div>
                      <p className="font-medium">{p.name}</p>
                      <p className="text-xs capitalize text-muted-foreground">{p.species} · {p.breed || '—'}</p>
                    </div>
                  </button>
                ))}
                {pets.length === 0 && (
                  <p className="py-8 text-center text-sm text-muted-foreground">No pets for this owner</p>
                )}
              </div>
              <Button variant="ghost" size="sm" onClick={() => setStep('owner')}>← Back</Button>
            </div>
          )}

          {step === 'reason' && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">Describe the emergency:</p>
              <textarea
                className="flex min-h-[100px] w-full rounded-lg border border-input bg-background p-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                placeholder="E.g., Hit by car, vomiting, difficulty breathing..."
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                autoFocus
              />
              <div className="flex gap-2">
                <Button variant="ghost" onClick={() => setStep('pet')}>← Back</Button>
                <Button className="flex-1 gap-2" onClick={handleSubmit} disabled={submitting}>
                  {submitting ? <><Loader2 size={16} className="animate-spin" /> Processing...</> : 'Check In Emergency'}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
