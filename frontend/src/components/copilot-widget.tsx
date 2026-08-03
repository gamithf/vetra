import { useState, useRef, useCallback } from 'react'
import { Mic, MicOff, Send, Loader2, ChevronDown, X, Headphones } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { transcriptionApi } from '@/lib/api'
import { DEMO_TRANSCRIPT } from '@/lib/constants'
import { sleep, formatCurrency } from '@/lib/format'
import { AgentStream, type AgentSummary } from '@/components/agent-stream'
import { toast } from 'sonner'

interface Props {
  activePatientId: string | null
  activePatientName?: string | null
  activeAppointmentId: string | null
  activeAppointmentReason?: string | null
  onNoteSubmitted: () => void
}

export function CopilotWidget({ activePatientId, activePatientName, activeAppointmentId, activeAppointmentReason, onNoteSubmitted }: Props) {
  const [expanded, setExpanded] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [agentOpen, setAgentOpen] = useState(false)
  const mediaRecorder = useRef<MediaRecorder | null>(null)
  const chunks = useRef<Blob[]>([])

  const locked = activePatientId !== null && activeAppointmentId !== null

  const handleTranscribe = useCallback(async (blob: Blob) => {
    setIsTranscribing(true)
    try {
      if (DEMO_TRANSCRIPT) {
        // Deterministic demo: show the exact dictated message (the narrator
        // reads this phrase aloud during the recording).
        await sleep(1300)
        setTranscript(DEMO_TRANSCRIPT)
        toast.success('Transcription ready — review before submitting')
      } else {
        const res = await transcriptionApi.transcribe(blob)
        if (res.text) {
          setTranscript(res.text)
          toast.success('Transcription ready — review before submitting')
        } else {
          toast.error('No speech detected')
        }
      }
    } catch {
      toast.error('Speech-to-text failed')
    } finally {
      setIsTranscribing(false)
    }
  }, [])

  const stopRecording = useCallback(() => {
    mediaRecorder.current?.stop()
    setIsRecording(false)
  }, [])

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      chunks.current = []
      recorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.current.push(e.data) }
      recorder.onstop = () => {
        const blob = new Blob(chunks.current, { type: 'audio/webm' })
        stream.getTracks().forEach((t) => t.stop())
        handleTranscribe(blob)
      }
      recorder.start()
      mediaRecorder.current = recorder
      setIsRecording(true)
      toast.info('Recording... stop to transcribe')
    } catch {
      toast.error('Microphone access denied')
    }
  }, [handleTranscribe])

  const handleSubmit = () => {
    if (!transcript.trim()) return toast.error('No notes to submit')
    if (!activeAppointmentId || !activePatientId) return toast.error('No active patient selected')
    setExpanded(false)
    setAgentOpen(true)
  }

  const handleAgentDone = (summary: AgentSummary) => {
    setAgentOpen(false)
    toast.success('Visit complete — records, inventory & bill updated')
    if (summary.invoice_total) {
      toast('Bill generated', { description: formatCurrency(summary.invoice_total) })
    }
    setTranscript('')
    onNoteSubmitted()
  }

  const busy = isRecording || isTranscribing

  return (
    <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-2">
      {expanded && (
        <div className="w-80 animate-in rounded-xl border bg-card shadow-xl">
          <div className="flex items-center justify-between border-b px-4 py-3">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Headphones size={16} className="text-primary" />
              AI Co-Pilot
            </div>
            <div className="flex items-center gap-1">
              {locked && (
                <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary">
                  LOCKED
                </span>
              )}
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => setExpanded(false)}>
                <X size={14} />
              </Button>
            </div>
          </div>

          <div className="space-y-3 p-4">
            {!locked && (
              <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700">
                Select a patient from the queue to enable note submission.
              </p>
            )}

            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground">Active Patient</p>
              <div className="flex items-center gap-2 text-sm">
                <span className={cn('h-2 w-2 rounded-full', locked ? 'bg-emerald-500' : 'bg-muted-foreground')} />
                {locked ? (activePatientName || `Patient #${activePatientId!.slice(0, 8)}`) : 'No patient selected'}
              </div>
            </div>

            {isRecording && (
              <div className="flex items-center justify-center gap-2 rounded-lg border border-primary/30 bg-primary/5 py-4">
                <span className="h-2 w-2 animate-pulse rounded-full bg-red-500" />
                <span className="text-xs font-medium text-primary">Listening...</span>
                <div className="flex h-8 items-end gap-0.5">
                  {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => (
                    <span
                      key={i}
                      className="w-1 animate-pulse rounded-full bg-primary"
                      style={{ height: `${10 + ((i * 7) % 25)}px`, animationDelay: `${i * 90}ms` }}
                    />
                  ))}
                </div>
              </div>
            )}

            {isTranscribing && (
              <div className="flex items-center justify-center gap-2 rounded-lg border border-violet-200 bg-violet-50 py-3">
                <Loader2 size={16} className="animate-spin text-violet-600" />
                <span className="text-xs font-medium text-violet-700">Converting speech to text...</span>
              </div>
            )}

            <textarea
              className="flex min-h-[100px] w-full rounded-lg border border-input bg-background p-3 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-60"
              placeholder={busy ? (isRecording ? 'Recording... edit disabled' : 'Converting...') : 'Type or dictate your clinical notes...'}
              value={transcript}
              readOnly={busy}
              disabled={busy}
              onChange={(e) => setTranscript(e.target.value)}
            />

            <div className="flex gap-2">
              <Button
                variant={isRecording ? 'destructive' : 'secondary'}
                size="sm"
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isTranscribing}
                className="gap-1.5"
              >
                {isRecording ? <MicOff size={14} /> : <Mic size={14} />}
                {isRecording ? 'Stop' : 'Record'}
              </Button>
              <Button
                size="sm"
                className="flex-1 gap-1.5"
                onClick={handleSubmit}
                disabled={busy || !locked || !transcript.trim()}
              >
                <Send size={14} />
                Submit
              </Button>
            </div>
          </div>
        </div>
      )}

      <button
        onClick={() => setExpanded(!expanded)}
        className={cn(
          'flex items-center gap-2 rounded-full px-5 py-3 text-sm font-medium shadow-lg transition-all',
          activePatientId ? 'bg-primary text-primary-foreground hover:opacity-90' : 'bg-muted text-muted-foreground hover:bg-accent',
          expanded && 'shadow-none',
        )}
      >
        {expanded ? <ChevronDown size={18} /> : <Mic size={18} />}
        {expanded ? 'Collapse' : 'AI Co-Pilot'}
        {!expanded && activePatientId && <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />}
      </button>

      <AgentStream
        open={agentOpen}
        onClose={() => setAgentOpen(false)}
        onDone={handleAgentDone}
        transcript={transcript}
        petId={activePatientId || ''}
        appointmentId={activeAppointmentId || ''}
        appointmentReason={activeAppointmentReason}
      />
    </div>
  )
}
