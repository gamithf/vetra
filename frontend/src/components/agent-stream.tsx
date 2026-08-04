import { useEffect, useRef, useState } from 'react'
import {
  Brain, CheckCircle2, ClipboardList, FileText, FolderOpen, Loader2,
  Package, Receipt, X,
} from 'lucide-react'
import { AGENT_WS_URL } from '@/lib/constants'
import { useAuth } from '@/context/auth-context'
import { cn } from '@/lib/utils'
import { formatCurrency } from '@/lib/format'

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
  const [thinking, setThinking] = useState<Record<string, string>>({})
  const [results, setResults] = useState<Record<string, string>>({})
  const [activeAgent, setActiveAgent] = useState<string | null>(null)
  const [summary, setSummary] = useState<AgentSummary | null>(null)
  const [error, setError] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement | null>(null)
  const liveRef = useRef<string | null>(null)

  useEffect(() => {
    if (!open) return
    setStates({})
    setDetails({})
    setThinking({})
    setResults({})
    setActiveAgent(null)
    setSummary(null)
    setError(null)
    liveRef.current = null

    const ws = new WebSocket(AGENT_WS_URL)
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
        if (msg.agent === liveRef.current || liveRef.current === null) {
          setThinking((t) => ({ ...t, [msg.agent]: (t[msg.agent] || '') + msg.text }))
        } else {
          setThinking((t) => ({ ...t, [msg.agent]: (t[msg.agent] || '') + msg.text }))
        }
      } else if (msg.type === 'agent') {
        setStates((s) => ({ ...s, [msg.agent]: msg.status }))
        if (msg.detail) setDetails((d) => ({ ...d, [msg.agent]: msg.detail }))
        if (msg.status === 'working' || msg.status === 'thinking') {
          liveRef.current = msg.agent
          setActiveAgent(msg.agent)
        } else if (msg.status === 'complete' && liveRef.current === msg.agent) {
          liveRef.current = null
        }
      } else if (msg.type === 'result') {
        setResults((r) => ({ ...r, [msg.agent]: msg.text }))
      } else if (msg.type === 'done') {
        setSummary(msg.summary)
        liveRef.current = null
        // Return to the summary view so the "Done" button is always reachable,
        // even if an agent's step is the last one viewed.
        setActiveAgent(null)
      } else if (msg.type === 'error') {
        setError(msg.detail)
        setActiveAgent(null)
      }
    }
    ws.onerror = () => setError('Agent service connection failed')
    return () => ws.close()
  }, [open, token, transcript, petId, appointmentId, appointmentReason, user?.id, user?.role])

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [thinking, activeAgent])

  if (!open) return null

  const done = summary !== null
  const view = activeAgent
  const viewState = view ? states[view] || 'pending' : 'pending'
  const viewThinking = view ? thinking[view] || '' : ''
  const viewResult = view ? results[view] : undefined
  const viewDetail = view ? details[view] : undefined
  const isLive = liveRef.current === view && (viewState === 'working' || viewState === 'thinking')
  const content = viewResult || (viewThinking ? viewThinking : (viewDetail || ''))

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="flex h-[560px] w-full max-w-2xl flex-col overflow-hidden rounded-2xl border bg-card shadow-2xl">
        <div className="flex items-center justify-between border-b px-5 py-3.5">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
              <Brain size={15} className="text-primary" />
            </span>
            Vetra Agent
          </div>
          <button
            onClick={onClose}
            disabled={!done}
            className={cn('rounded-md p-1 text-muted-foreground hover:bg-accent', !done && 'opacity-40')}
          >
            <X size={16} />
          </button>
        </div>

        <div className="grid flex-1 grid-cols-[200px_1fr] overflow-hidden">
          <aside className="border-r bg-muted/20 p-3">
            <p className="mb-2 px-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Agents Pipeline
            </p>
            <ul className="space-y-1">
              {AGENTS.map((a) => {
                const st = states[a.key] || 'pending'
                const isActive = view === a.key
                return (
                  <li key={a.key}>
                    <button
                      onClick={() => setActiveAgent(a.key)}
                      className={cn(
                        'flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-xs transition-colors',
                        isActive ? 'bg-primary/10 text-primary' : 'hover:bg-accent cursor-pointer',
                        st === 'pending' && !isActive && 'text-muted-foreground/60',
                        st === 'complete' && !isActive && 'text-muted-foreground',
                      )}
                    >
                      {statusIcon(st)}
                      <span className="flex items-center gap-1.5 truncate">
                        {a.icon}
                        {a.label}
                      </span>
                    </button>
                  </li>
                )
              })}
            </ul>
          </aside>

          <div className="flex min-w-0 flex-col p-5">
            {error ? (
              <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center">
                <X className="text-red-500" size={28} />
                <p className="text-sm font-medium text-red-600">Agent pipeline failed</p>
                <p className="max-w-sm break-words text-xs text-muted-foreground">{error}</p>
                <button onClick={onClose} className="mt-1 rounded-lg border px-3 py-1.5 text-xs font-medium hover:bg-accent">
                  Close
                </button>
              </div>
            ) : done && !view ? (
              <div className="flex flex-1 flex-col">
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-emerald-600">
                    <CheckCircle2 size={20} />
                    <p className="text-sm font-semibold">Visit processed successfully</p>
                  </div>
                  <div className="space-y-2 rounded-lg border p-3">
                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">Diagnosis</p>
                      <p className="text-sm">{summary.diagnosis}</p>
                    </div>
                    <div>
                      <p className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">Treatment</p>
                      <p className="text-sm">{summary.treatment}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {typeof summary.invoice_total === 'number' && (
                      <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                        Bill: {formatCurrency(summary.invoice_total)}
                      </span>
                    )}
                    {summary.inventory_log.map((line) => (
                      <span key={line} className="rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
                        {line}
                      </span>
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Click any agent on the left to review exactly what it did.
                  </p>
                </div>
                <button
                  onClick={() => onDone(summary)}
                  className="mt-auto w-full rounded-lg bg-primary py-2.5 text-sm font-medium text-primary-foreground hover:opacity-90"
                >
                  Done
                </button>
              </div>
            ) : (
              <div className="flex min-h-0 flex-1 flex-col">
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    {view ? (AGENTS.find((a) => a.key === view)?.label || view) : 'Agents working...'}
                  </p>
                  {isLive && (
                    <span className="flex items-center gap-1.5 text-[10px] font-medium text-primary">
                      <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary" /> LIVE
                    </span>
                  )}
                </div>
                <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto rounded-lg border bg-muted/40 p-3">
                  <p className="whitespace-pre-wrap text-[13px] leading-relaxed text-foreground/90">
                    {content || 'Waiting for this agent to run...'}
                    {isLive && <span className="ml-1 inline-block h-3.5 w-1.5 animate-pulse bg-primary align-middle" />}
                  </p>
                </div>
                {view && !viewResult && viewThinking && (
                  <p className="mt-2 text-[10px] text-muted-foreground">
                    {viewState === 'complete' ? 'Streamed reasoning from this step.' : 'Streaming reasoning...'}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
