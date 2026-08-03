import { useEffect, useRef, useState } from 'react'
import {
  Mic, BrainCircuit, Stethoscope, ClipboardList, Database, Package, Calculator,
  Loader2, CheckCircle2, Sparkles,
} from 'lucide-react'
import { sleep } from '@/lib/demo'
import { cn } from '@/lib/utils'

export interface AgentStep {
  key: string
  label: string
  detail: string
  icon: React.ReactNode
}

export const PIPELINE_STEPS: AgentStep[] = [
  { key: 'transcribe', label: 'Transcribing', detail: 'Converting the vet\'s voice to text', icon: <Mic size={18} /> },
  { key: 'analyze', label: 'Analyzing Symptoms', detail: 'Extracting symptoms from the consultation', icon: <BrainCircuit size={18} /> },
  { key: 'diagnose', label: 'Generating Diagnosis & Plan', detail: 'Reasoning a treatment plan from the findings', icon: <Stethoscope size={18} /> },
  { key: 'record', label: 'Creating Medical Record', detail: 'Appending the structured note to the EMR', icon: <ClipboardList size={18} /> },
  { key: 'inventory', label: 'Updating Inventory', detail: 'Deducting supplies used during the visit', icon: <Package size={18} /> },
  { key: 'bill', label: 'Calculating Bill', detail: 'Preparing the invoice for checkout', icon: <Calculator size={18} /> },
]

interface Props {
  open: boolean
  onComplete: () => void
  patientName?: string
}

export function AgentPipeline({ open, onComplete, patientName }: Props) {
  const [current, setCurrent] = useState(-1)
  const [done, setDone] = useState(false)
  const finishedRef = useRef(false)

  useEffect(() => {
    if (!open) {
      setCurrent(-1)
      setDone(false)
      finishedRef.current = false
      return
    }
    let cancelled = false
    ;(async () => {
      for (let i = 0; i < PIPELINE_STEPS.length; i++) {
        if (cancelled) return
        setCurrent(i)
        await sleep(850)
      }
      if (cancelled) return
      setDone(true)
      await sleep(1100)
      if (cancelled) return
      if (!finishedRef.current) {
        finishedRef.current = true
        onComplete()
      }
    })()
    return () => { cancelled = true }
  }, [open, onComplete])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md animate-in rounded-2xl border bg-card p-6 shadow-2xl">
        <div className="mb-5 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10">
            <Sparkles size={22} className="text-primary" />
          </div>
          <div>
            <h3 className="text-base font-semibold">AI Co-Pilot Agents</h3>
            <p className="text-xs text-muted-foreground">
              {patientName ? `Processing visit for ${patientName}` : 'Processing the consultation'}
            </p>
          </div>
        </div>

        <div className="mb-5 h-1.5 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary transition-all duration-500"
            style={{ width: done ? '100%' : `${((current + 1) / PIPELINE_STEPS.length) * 100}%` }}
          />
        </div>

        <div className="space-y-2">
          {PIPELINE_STEPS.map((step, i) => {
            const isActive = i === current && !done
            const isDone = i < current || done
            return (
              <div
                key={step.key}
                className={cn(
                  'flex items-center gap-3 rounded-xl border px-3 py-2.5 transition-all duration-300',
                  isActive && 'border-primary/40 bg-primary/5 shadow-sm',
                  isDone && 'border-emerald-200/60 bg-emerald-50/40',
                  !isActive && !isDone && 'border-input opacity-50',
                )}
              >
                <div className={cn(
                  'flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-colors',
                  isDone ? 'bg-emerald-100 text-emerald-600' : isActive ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground',
                )}>
                  {isDone ? <CheckCircle2 size={18} /> : isActive ? <Loader2 size={18} className="animate-spin" /> : step.icon}
                </div>
                <div className="min-w-0 flex-1">
                  <p className={cn('text-sm font-medium', isDone ? 'text-emerald-800' : 'text-foreground')}>{step.label}</p>
                  <p className="truncate text-xs text-muted-foreground">{isDone ? 'Done' : step.detail}</p>
                </div>
                {isActive && (
                  <div className="flex gap-0.5">
                    {[0, 1, 2].map((b) => (
                      <span
                        key={b}
                        className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary"
                        style={{ animationDelay: `${b * 150}ms` }}
                      />
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {done && (
          <div className="mt-5 animate-in flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3">
            <Database size={18} className="text-emerald-600" />
            <p className="text-sm font-medium text-emerald-800">All agents finished — visit is fully recorded.</p>
          </div>
        )}
      </div>
    </div>
  )
}
