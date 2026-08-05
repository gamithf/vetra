import { useEffect, useRef, useState } from 'react'
import {
  Brain, CheckCircle2, ClipboardList, FileText, FolderOpen, Loader2,
  Package, Receipt, ShieldAlert, ShieldCheck, X,
} from 'lucide-react'
import { AGENT_WS_URL } from '@/lib/constants'
import { useAuth } from '@/context/auth-context'
import { cn } from '@/lib/utils'
import { formatCurrency } from '@/lib/format'

export interface SafetyAlert {
  drug_a: string
  drug_b: string
  severity: 'high' | 'medium' | 'low'
  summary: string
  guidance: string
}

export interface AgentSummary {
  diagnosis: string
  treatment: string
  record_id?: string
  note_id?: string
  invoice_total?: number
  inventory_log: string[]
  safety?: {
    risk_level: 'high' | 'medium' | 'low'
    alerts: SafetyAlert[]
    summary?: string
  }
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
  { key: 'safety', label: 'Clinical Safety (RAG)', icon: <ShieldCheck size={16} /> },
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
  const [safety, setSafety] = useState<{ risk_level: 'high' | 'medium' | 'low'; alerts: SafetyAlert[]; summary?: string } | null>(null)
  const [safetyAcked, setSafetyAcked] = useState(false)
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
    setSafety(null)
    setSafetyAcked(false)
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
      } else if (msg.type === 'safety') {
        setSafety(msg)
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

  const riskLevel = safety?.risk_level
  const safetyAlerts = safety?.alerts || []
  const highBlocked = riskLevel === 'high' && !safetyAcked

  const safetyBanner =
    riskLevel === 'high'
      ? { cls: 'border-red-200 bg-red-50 text-red-700', icon: <ShieldAlert size={18} className="mt-0.5 shrink-0 text-red-500" />, title: 'HIGH-RISK DRUG INTERACTION DETECTED' }
      : riskLevel === 'medium'
        ? { cls: 'border-amber-200 bg-amber-50 text-amber-700', icon: <ShieldAlert size={18} className="mt-0.5 shrink-0 text-amber-500" />, title: 'Potential drug interaction' }
        : { cls: 'border-emerald-200 bg-emerald-50 text-emerald-700', icon: <ShieldCheck size={18} className="mt-0.5 shrink-0 text-emerald-500" />, title: 'Clinical safety check passed' }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="flex h-[560px] w-full max-w-2xl flex-col overflow-hidden rounded-2xl border bg-card shadow-2xl">
        <div className="flex items-center justify-between border-b px-5 py-3.5">
          <div className="flex items-center gap-2 text-sm font-semibold uppercase justify-center">
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

        {safety && !highBlocked && (
          <div className={cn('flex items-start gap-2.5 border-b px-5 py-3 text-xs', safetyBanner.cls)}>
            {safetyBanner.icon}
            <div className="min-w-0">
              <p className="text-[11px] font-bold uppercase tracking-wide">{safetyBanner.title}</p>
              <p className="mt-0.5 text-[11px] opacity-90">{safety.summary}</p>
              {safetyAlerts.map((a, i) => (
                <p key={i} className="mt-1 text-[11px] opacity-90">
                  {a.drug_a} + {a.drug_b} — {a.severity.toUpperCase()}: {a.summary}
                </p>
              ))}
            </div>
          </div>
        )}

        {highBlocked && (
          <div className="flex flex-1 items-center justify-center p-6">
            <div className="w-full max-w-md rounded-2xl border-2 border-red-500 bg-white p-6 shadow-2xl">
              <div className="flex items-start gap-3">
                <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-red-100">
                  <ShieldAlert size={26} className="text-red-600" />
                </span>
                <div className="min-w-0">
                  <p className="text-sm font-bold uppercase tracking-wide text-red-600">High-risk drug interaction</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    The Clinical Safety agent flagged a critical interaction against the patient's medication history.
                  </p>
                </div>
              </div>
              <div className="mt-4 space-y-2.5">
                {safetyAlerts.map((a, i) => (
                  <div key={i} className="rounded-xl border border-red-200 bg-red-50 p-3">
                    <p className="text-sm font-bold text-red-700">
                      {a.drug_a} + {a.drug_b} — HIGH
                    </p>
                    <p className="mt-1 text-xs text-red-700/90">{a.summary}</p>
                    <p className="mt-1.5 text-[11px] font-medium text-red-700/80">Recommendation: {a.guidance}</p>
                  </div>
                ))}
              </div>
              <button
                onClick={() => setSafetyAcked(true)}
                className="mt-5 w-full cursor-pointer rounded-lg bg-red-600 py-2.5 text-sm font-bold text-white hover:bg-red-700"
              >
                Acknowledge & continue
              </button>
            </div>
          </div>
        )}

        {!highBlocked && (
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
                    {summary.safety && (
                      <span
                        className={cn(
                          'rounded-full px-2.5 py-1 text-xs font-medium',
                          summary.safety.risk_level === 'high' && 'bg-red-50 text-red-600',
                          summary.safety.risk_level === 'medium' && 'bg-amber-50 text-amber-600',
                          summary.safety.risk_level === 'low' && 'bg-emerald-50 text-emerald-600',
                        )}
                      >
                        Safety:{' '}
                        {summary.safety.risk_level === 'high'
                          ? `${summary.safety.alerts.length} interaction(s) flagged`
                          : summary.safety.risk_level === 'medium'
                            ? 'Interaction flagged'
                            : 'No interactions found'}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Click any step on the left to review details
                  </p>
                </div>
                <button
                  onClick={() => onDone(summary)}
                  className="mt-auto w-full rounded-lg bg-primary py-2.5 text-sm font-medium text-primary-foreground hover:opacity-90 cursor-pointer transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
        )}
      </div>
    </div>
  )
}
