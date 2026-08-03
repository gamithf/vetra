import { useState, useRef, useCallback } from 'react'
import { Mic, MicOff, Send, Loader2, ChevronDown, X, Headphones, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useApi } from '@/lib/use-api'
import { isDemo, sleep } from '@/lib/demo'
import { AgentPipeline } from '@/components/agent-pipeline'
import { toast } from 'sonner'

interface Props {
  activePatientId: string | null
  activePatientName?: string | null
  activeAppointmentId: string | null
  onNoteSubmitted: () => void
}

const DEMO_TRANSCRIPT =
  'Max is a 5-year-old male Golden Retriever here for his annual wellness exam. Owner reports he has been eating well and is active, with no concerns. Physical exam: temperature 101.2F, heart rate 80, respiratory rate 20. Eyes clear, ears clean, teeth show mild tartar. Heart and lungs auscultated normal. Abdomen soft. Recommended dental cleaning. DAPP vaccination updated.'

export function CopilotWidget({ activePatientId, activePatientName, activeAppointmentId, onNoteSubmitted }: Props) {
  const { clinicalNotesApi } = useApi()
  const [expanded, setExpanded] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [pipelineOpen, setPipelineOpen] = useState(false)
  const mediaRecorder = useRef<MediaRecorder | null>(null)
  const chunks = useRef<Blob[]>([])
  const recordingTimer = useRef<number | null>(null)

  const locked = activePatientId !== null
  const demo = isDemo()

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      chunks.current = []
      recorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.current.push(e.data) }
      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop())
      }
      recorder.start()
      mediaRecorder.current = recorder
      setIsRecording(true)

      // In demo mode, auto-populate the transcript after ~4s of "recording"
      if (demo) {
        recordingTimer.current = window.setTimeout(() => {
          stopRecording()
          setTranscript(DEMO_TRANSCRIPT)
          toast.success('Transcription ready — review before submitting')
        }, 4000)
      } else {
        toast.info('Recording... Speak your findings')
      }
    } catch {
      toast.error('Microphone access denied')
    }
  }, [demo])

  const stopRecording = () => {
    mediaRecorder.current?.stop()
    setIsRecording(false)
    if (recordingTimer.current) {
      clearTimeout(recordingTimer.current)
      recordingTimer.current = null
    }
  }

  const handleSubmit = async () => {
    if (!transcript.trim()) return toast.error('No notes to submit')
    if (!activeAppointmentId) return toast.error('No active patient selected')

    setSubmitting(true)
    try {
      if (demo) {
        // Showcase the simulated multi-agent pipeline
        setExpanded(false)
        await sleep(250)
        setPipelineOpen(true)
      } else {
        const res = await clinicalNotesApi.create({
          pet_id: activePatientId!,
          appointment_id: activeAppointmentId,
          raw_transcript: transcript,
        })
        toast.success(res.message)
        setTranscript('')
        onNoteSubmitted()
      }
    } catch {
      toast.error('Failed to submit notes')
    } finally {
      setSubmitting(false)
    }
  }

  const handlePipelineComplete = async () => {
    setPipelineOpen(false)
    try {
      const res = await clinicalNotesApi.create({
        pet_id: activePatientId!,
        appointment_id: activeAppointmentId,
        raw_transcript: transcript,
      })
      toast.success(res.message)
      toast('Inventory updated', { description: 'Supplies deducted for this visit' })
      setTranscript('')
      onNoteSubmitted()
    } catch {
      toast.error('Failed to submit notes')
    }
  }

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
              {demo && (
                <span className="flex items-center gap-1 rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-medium text-violet-700">
                  <Sparkles size={10} /> SIMULATED
                </span>
              )}
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
              <div className="flex items-center justify-center gap-1 rounded-lg border border-primary/30 bg-primary/5 py-4">
                <span className="h-2 w-2 animate-pulse rounded-full bg-red-500" />
                <span className="text-xs font-medium text-primary">Listening...</span>
                <div className="flex h-8 items-end gap-0.5">
                  {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => (
                    <span
                      key={i}
                      className="w-1 animate-pulse rounded-full bg-primary"
                      style={{
                        height: `${10 + ((i * 7) % 25)}px`,
                        animationDelay: `${i * 90}ms`,
                      }}
                    />
                  ))}
                </div>
              </div>
            )}

            <textarea
              className="flex min-h-[100px] w-full rounded-lg border border-input bg-background p-3 text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              placeholder={isRecording ? 'Recording...' : 'Type or dictate your clinical notes...'}
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
            />

            <div className="flex gap-2">
              <Button
                variant={isRecording ? 'destructive' : 'secondary'}
                size="sm"
                onClick={isRecording ? stopRecording : startRecording}
                className="gap-1.5"
              >
                {isRecording ? <MicOff size={14} /> : <Mic size={14} />}
                {isRecording ? 'Stop' : 'Record'}
              </Button>
              <Button
                size="sm"
                className="flex-1 gap-1.5"
                onClick={handleSubmit}
                disabled={submitting || !locked || !transcript.trim()}
              >
                {submitting ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
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

      <AgentPipeline
        open={pipelineOpen}
        onComplete={handlePipelineComplete}
        patientName={activePatientName || undefined}
      />
    </div>
  )
}
