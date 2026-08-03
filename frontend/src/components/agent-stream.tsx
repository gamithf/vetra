import { useEffect, useRef, useState } from 'react'
import {
  Brain, CheckCircle2, ClipboardList, FileText, FolderOpen, Loader2,
  Package, Receipt, X,
} from 'lucide-react'
import { agentWsUrl } from '@/lib/api'
import { useAuth } from '@/context/auth-context'
import { cn } from '@/lib/utils'

export interface AgentSummary {
  diagnosis: string
  treatment: string
  record_id?: string
  note_id?: string
  invoice_total?: number
  inventory_log: string[]
}

interface Props {
  open: boolean
  transcript: string
  petId: string
  appointmentId: string
  appointmentReason?: string | null
  onClose: () => void
  onDone: (summary: AgentSummary) => void
}

type AgentState = 'working' | 'thinking' | 'complete' | 'pending'

const AGENTS: { key: string; label: string; icon: React.ReactNode }[] = [
  { key: 'context', label: 'Patient Context', icon: <FolderOpen size={16} /> },
  { key: 'medical', label: 'Medical Reasoning', icon: <Brain size={16} /> },
  { key: 'notes', label: 'Clinical Note', icon: <FileText size={16} /> },
  { key: 'records', label: 'Medical Record', icon: <ClipboardList size={16} /> },
  { key: 'inventory', label: 'Inventory', icon: <Package size={16} /> },
  { key: 'billing', label: 'Billing', icon: <Receipt size={16} /> },
  { key: 'finalize', label: 'Finalize', icon: <CheckCircle2 size={16} /> },
]

function statusIcon(status: AgentState) {
  if (status === 'working' || status === 'thinking') {
    return <Loader2 size={15} className="animate-spin text-primary" />
  }
  if (status === 'complete') {
    return <CheckCircle2 size={15} className="text-emerald-500" />
  }
  return <span className="h-3.5 w-3.5 rounded-full border-2 border-muted-foreground/30" />
}

export function AgentStream({ open, transcript, petId, appointmentId, appointmentReason, onClose, onDone }: Props) {
  const { token, user } = useAuth()
  const [states, setStates] = useState<Record<string, AgentState>>({})
  const [details, setDetails] = useState<Record<string, string>>({})
  const [thinking, setThinking] = useState('')
  const [currentAgent, setCurrentAgent] = useState<string | null>(null)
  const [summary, setSummary] = useState<AgentSummary | null>(null)
  const [error, setError] = useState<string | null>(null)
  const currentRef = useRef<string | null>(null)
  const doneRef = useRef(false)

  useEffect(() => {
    if (!open) return
    setStates({})
    setDetails({})
    setThinking('')
    setCurrentAgent(null)
    setSummary(null)
    setError(null)
    doneRef.current = false
    currentRef.current = null

    const ws = new WebSocket(agentWsUrl)
    ws.onopen = () => {
      ws.send(JSON.stringify({
        type: 'run',
        token,
        pet_id: petId,
        appointment_id: appointmentId,
        vet_id: user?.role === 'vet' ? user.id : undefined,
        reason: appointmentReason || undefined,
        transcript,
      }))
    }
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.type === 'thinking') {
        if (msg.agent !== currentRef.current) {
          currentRef.current = msg.agent
          setCurrentAgent(msg.agent)
          setThinking('')
        }
        setThinking((t) => t + msg.text)
      } else if (msg.type === 'agent') {
        currentRef.current = msg.agent
        setCurrentAgent(msg.agent)
        setStates((s) => ({ ...s, [msg.agent]: msg.status }))
        if (msg.detail) setDetails((d) => ({ ...d, [msg.agent]: msg.detail }))
        if (msg.status === 'working' || msg.status === 'thinking') setThinking('')
      } else if (msg.type === 'done') {
        setSummary(msg.summary)
        doneRef.current = true
      } else if (msg.type === 'error') {
        setError(msg.detail)
      }
    }
    ws.onerror = () => setError('Agent service connection failed')
    return () => ws.close()
  }, [open, token, transcript, petId, appointmentId, appointmentReason, user?.id, user?.role])

  const done = summary !== null
  const currentDetail = currentAgent ? details[currentAgent] : null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="flex w-full max-w-2xl flex-col overflow-hidden rounded-2xl border bg-card shadow-2xl">
        <div className="flex items-center justify-between border-b px-5 py-3.5">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <Brain size={16} className="text-primary" />
            Vetra Agent Pipeline
          </div>
          <ButtonGhost onClose={onClose} done={done} />
        </div>

        <div className="grid grid-cols-[200px_1fr]">
          <div className="border-r p-3">
            <ul className="space-y-1">
              {AGENTS.map((a) => {
                const st = states[a.key] || 'pending'
                return (
                  <li
                    key={a.key}
                    className={cn(
                      'flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs',
                      (st === 'working' || st === 'thinking') && 'bg-primary/10 text-primary',
                      (st === 'complete') && 'text-muted-foreground',
                      st === 'pending' && 'text-muted-foreground/60',
                    )}
                  >
                    {statusIcon(st)}
                    <span className="flex items-center gap-1.5">
                      {a.icon}
                      {a.label}
                    </span>
                  </li>
                )
              })}
            </ul>
          </div>

          <div className="min-h-[260px] p-5">
            {error ? (
              <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
                <X className="text-red-500" size={28} />
                <p className="text-sm font-medium text-red-600">Agent pipeline failed</p>
                <p className="max-w-sm text-xs text-muted-foreground">{error}</p>
                <button onClick={onClose} className="mt-1 rounded-lg border px-3 py-1.5 text-xs font-medium hover:bg-accent">
                  Close
                </button>
              </div>
            ) : done && summary ? (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-emerald-600">
                  <CheckCircle2 size={20} />
                  <p className="text-sm font-semibold">Visit processed successfully</p>
                </div>
                <div className="space-y-2">
                  <div>
                    <p className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">Diagnosis</p>
                    <p className="text-sm">{summary.diagnosis}</p>
                  </div>
                  <div>
                    <p className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">Treatment</p>
                    <p className="text-sm">{summary.treatment}</p>
                  </div>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {typeof summary.invoice_total === 'number' && (
                      <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                        Bill: ${summary.invoice_total.toFixed(2)}
                      </span>
                    )}
                    {summary.inventory_log.map((line) => (
                      <span key={line} className="rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
                        {line}
                      </span>
                    ))}
                  </div>
                </div>
                <button
                  onClick={() => onDone(summary)}
                  className="w-full rounded-lg bg-primary py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
                >
                  Done
                </button>
              </div>
            ) : (
              <div className="flex h-full flex-col">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  {currentAgent ? `${currentAgent} agent` : 'Agents working...'}
                </p>
                <div className="flex-1 overflow-y-auto rounded-lg border bg-muted/40 p-3">
                  <p className="whitespace-pre-wrap text-[13px] leading-relaxed text-foreground/90">
                    {thinking || currentDetail || 'Initializing pipeline...'}
                    {currentAgent === 'medical' && !thinking && currentDetail ? <span className="ml-1 inline-block h-3.5 w-1.5 animate-pulse bg-primary align-middle" /> : null}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function ButtonGhost({ onClose, done }: { onClose: () => void; done: boolean }) {
  return (
    <button onClick={onClose} disabled={!done} className={cn('rounded-md p-1 text-muted-foreground hover:bg-accent', !done && 'opacity-40')}>
      <X size={16} />
    </button>
  )
}
