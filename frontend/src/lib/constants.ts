export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const API_PREFIX = '/api/v1'

export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

export const AGENT_WS_URL = import.meta.env.VITE_AGENT_URL || 'ws://localhost:8001/agent'

// The exact phrase the vet dictates during the recorded demo. On "Stop", the
// co-pilot shows this transcript so the demo is deterministic.
export const DEMO_TRANSCRIPT =
  "Cooper has atopic dermatitis. Prescribe Amoxicillin 250mg. Check if Meloxicam interacts with Cooper's current medications. Dispensed Amoxicillin 250mg. Schedule follow-up in 7 days."
